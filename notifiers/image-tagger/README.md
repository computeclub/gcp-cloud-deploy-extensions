# image-tagger

A Cloud Depoloy notifier to tag images following successful rollout operations.

## User story

As an engineer, I want a successful rollout to an environment target to result
in tags being added to the successfully deployed container image in a registry.
A moving tag of `<ENV>-current` gives an at-a-glance view of what is currently
deployed where when looking at a list of images in the registry. Likewise, tags
having `<ENV>-<SHORT_SHA>` provide a historical record of what was previously
deployed successfully to a target. Tagging should be supported within both
Artifact Registry and Google Container Registry (legacy).

## Configuration schema

`enabled` - a boolean that enables or disables the notifier. If not present the notifier is disabled.
`tags` (optional) - the set of tags to apply to all successful deployments. If not specified, both "${ENVIRONMENT}-${SHORT_SHA}", and "${ENVIRONMENT}-current" will be used.

Example:

```json
{
    "enabled": true,
    "tag_templates": [
        "${ENVIRONMENT}-current",
        "${ENVIRONMENT}-${SHORT_SHA}"
    ]
}
```

## Specifying template variable values

Tag template variable values (e.g. ${ENVIRONMENT} above) are fetched from
the annotations of the deployment target. If not found, the tag with a missing
value will not be applied to the container image and a log message will be
emitted.

## Built-in template variable values

Certain template variable values are always available and can't be overridden by
target labels. For now those are:

`SHORT_SHA` - the annotated 8 byte hash of the container image.
`FULL_SHA` - the full 40 byte hash of the container image.

## Author's confessional

### latest tags

It's fairly well established that deploying the `latest` tag of a container image
is not a best practice since container image tags are mutable. The examples in
this repo create manifests that render and deploy `latest` images to Cloud Run
environments, making a notifier like this more necessary. If that gap can be
closed via skaffold (e.g. if skaffold can create and use `<ENV>-<SHORT_SHA>`
tags), that would be a more ideal starting point than rendering manifests that
reference `latest` images. Even if skaffold closes that gap the solution here is
valuable because tagging after a deployment is validated is useful (i.e. it
creates a trail of deployed artifacts in a registry) and not otherwise achievable
without custom tooling.
