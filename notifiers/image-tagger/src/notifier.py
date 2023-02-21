# -*- coding: utf-8 -*-
import logging
import re
from typing import Any, Dict

from clouddeploy_notifier.notifier import BaseNotifier
from google.cloud import artifactregistry, deploy
from google.api_core.exceptions import AlreadyExists
from google.cloud.deploy_v1.types import (
    GetReleaseRequest,
    Release,
    GetTargetRequest,
    Target,
)
from google.cloud.artifactregistry_v1.types import (
    GetDockerImageRequest,
    ListDockerImagesRequest,
    CreateTagRequest,
    UpdateTagRequest,
    Tag,
)

logger = logging.getLogger(__name__)
# TODO(bjb): tag gcr.io images using the method described here: https://stackoverflow.com/questions/61465794/docker-sdk-with-google-container-registry


class Notifier(BaseNotifier):
    """Notifier tags images based on configuration."""

    @staticmethod
    def get_docker_image_components(release: Release):
        image_tag_split = release.build_artifacts[0].tag.split(":")
        image_url_parts, image_url, tag = (
            image_tag_split[0].split("/"),
            image_tag_split[0],
            image_tag_split[1],
        )
        location, project_id, repo_id, image_id = (
            image_url_parts[0].split("-docker")[0],
            image_url_parts[1],
            image_url_parts[2],
            image_url_parts[3],
        )
        repo_name = f"projects/{project_id}/locations/{location}/repositories/{repo_id}"
        image_name = f"{repo_name}/dockerImages/{image_id}"
        image_name_in_package_format = image_name.replace("dockerImages", "packages")
        return {
            "image_name": image_name,
            "repo_name": repo_name,
            "image_name_in_package_format": image_name_in_package_format,
            "image_url": image_url,
            "project_id": project_id,
            "location": location,
            "repo_id": repo_id,
            "image_id": image_id,
            "tag": tag,
        }

    @staticmethod
    def fetch_docker_image(image_url: str, repo_name: str):
        """
        fetch_docker_image.
        """
        registry_client = artifactregistry.ArtifactRegistryClient()
        list_request = ListDockerImagesRequest(parent=repo_name)
        while True:
            response = registry_client.list_docker_images(request=list_request)
            for image in response.docker_images:
                if "latest" in image.tags and image.uri.startswith(
                    image_url + "@sha256:"
                ):
                    image_request = GetDockerImageRequest(name=image.name)
                    return registry_client.get_docker_image(request=image_request)
            if response.next_page_token:
                list_request = ListDockerImagesRequest(
                    parent=repo_name,
                    page_token=response.next_page_token,
                )
                continue
            return None

    def action(self, config: Dict[str, Any], **_):
        """."""
        logging.debug("executing the action")

        if "tag_templates" not in config:
            logger.info(
                'This notifier is enabled but the "tag_templates" key was not found in the config secret. Not setting any tags and exiting.'
            )
            return None

        registry_client = artifactregistry.ArtifactRegistryClient()
        # Get the release to parse annotations. The annotations contain subsitution values
        deploy_client = deploy.CloudDeployClient()
        release_request = GetReleaseRequest(
            name=f"projects/{self.attributes.ProjectNumber}/locations/{self.attributes.Location}/deliveryPipelines/{self.attributes.DeliveryPipelineId}/releases/{self.attributes.ReleaseId}"
        )
        release = deploy_client.get_release(request=release_request)
        image_dict = self.get_docker_image_components(release=release)

        target_request = GetTargetRequest(
            name=f"projects/{self.attributes.ProjectNumber}/locations/{self.attributes.Location}/targets/{self.attributes.TargetId}"
        )

        try:
            target: Target = deploy_client.get_target(request=target_request)
        except Exception as err:
            logger.exception(err)
            return None

        annotations: Dict[str, str] = dict(target.annotations)

        if "image_name" in annotations:
            image_request = GetDockerImageRequest(name=annotations["image_name"])
            image = registry_client.get_docker_image(request=image_request)
        else:
            image = self.fetch_docker_image(
                image_url=image_dict["image_url"],
                repo_name=image_dict["repo_name"],
            )
            # TODO(bjb): The API for this doesn't exist yet but when it does use
            # update_release() method to store the image.name as image_name in
            # release annotations for future runs
        if not image:
            return None
        (
            image_dict["digest"],
            image_dict["image_name_no_digest"],
            image_dict["image_name_packages_versions_format_with_digest"],
            image_dict["image_name_packages_format_no_digest"],
        ) = (
            image.name.split("@")[1],
            image.name.split("@")[0],
            image.name.replace("dockerImages", "packages").replace("@", "/versions/"),
            image.name.replace("dockerImages", "packages").split("@")[0],
        )

        replacements = annotations.copy()
        replacements["LONG_SHA"] = image.uri.split("@")[-1].split(":")[1]
        replacements["SHORT_SHA"] = replacements["LONG_SHA"][0:8]
        new_tag_set = []
        # a regex pattern matching all text within the moustache of '${}'
        # (?<=\${) is a positive lookbehind that matches the characters ${ without including them in the final match.
        # [^{}]* matches any characters that are not { or } (i.e. the characters within the brackets).
        # (?=}) is a positive lookahead that matches the closing bracket } without including it in the final match.
        pattern = r"(?<=\${)[^{}]*(?=})"
        for tag_template in config["tag_templates"]:
            matches = re.findall(pattern, tag_template)
            # verify all matches are found in replacements
            if not all(key in replacements for key in matches):
                logger.info(
                    "Skipping tag template %s. One or more replacement vars in %s not found in the target annotation keys %s",
                    tag_template,
                    matches,
                    replacements.keys(),
                )
                continue
            for match in matches:
                tag_template = tag_template.replace(
                    "${%s}" % match, replacements[match]
                )
            new_tag_set.append(tag_template)

        for _tag in new_tag_set:
            # thank you https://blog.unit410.com/sre/security/2022/12/06/artifact-management-google-cloud.html
            tag = Tag(
                name=f"{image_dict['image_name_packages_format_no_digest']}/tags/{_tag}",
                version=image_dict["image_name_packages_versions_format_with_digest"],
            )
            create_tag_request = CreateTagRequest(
                parent=image_dict["image_name_packages_format_no_digest"],
                tag=tag,
                tag_id=_tag,
            )
            try:
                registry_client.create_tag(request=create_tag_request)
            except AlreadyExists as err:
                logger.info("Tag already exists, moving the tag instead: %s", err)
                update_tag_request = UpdateTagRequest(
                    tag=tag,
                )
                registry_client.update_tag(request=update_tag_request)
                logger.info("Tag updated successfully")
        logger.info("Tagging complete for image %s", image.name)
