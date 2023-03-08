# -*- coding: utf-8 -*-
"""This is an example Cloud Deploy app responder."""
import logging
import os
import subprocess

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import hcl
from google.cloud import secretmanager
from google.api_core.exceptions import PermissionDenied, NotFound
from google.cloud.secretmanager_v1.types import AccessSecretVersionRequest

logger = logging.getLogger(__name__)
app: FastAPI = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
TG_DIR = os.getcwd() + os.sep + ".." + os.sep + "terragrunt" + os.sep
ROOT_CONFIG_PATH = TG_DIR + os.sep + "config.hcl.json"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    dir_objects = [
        f for f in os.scandir(TG_DIR) if f.is_dir() and f.name != ".terraform"
    ]
    dirs_dict = {f.name: {} for f in dir_objects}
    for dir_name, dir_data in dirs_dict.items():
        if not dir_name.endswith("-extension"):
            dir_data["secret_set"] = "N/A"
        else:
            # TODO: check if the secret exists
            dir_data["secret_set"] = True
        if not os.path.isfile(f"{TG_DIR}{os.sep}{dir_name}{os.sep}.tg_state"):
            dir_data["terragrunt_applied"] = False
        else:
            dir_data["terragrunt_applied"] = True
    if os.path.isfile(ROOT_CONFIG_PATH):
        with open(ROOT_CONFIG_PATH, "r") as fp:
            root_config = hcl.load(fp)
    else:
        root_config = {}
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "dirs_dict": dirs_dict,
            "tg_dir": TG_DIR,
            "root_config": root_config,
        },
    )


@app.get("/workspace/{dir_name}")
async def get_workspace(request):
    return templates.TemplateResponse(
        "workspace.html",
        {
            "request": request,
            # "dir_name": dir_name,
        },
    )


@app.post("/workspace/{dir_name}/configure")
async def configure_workspace(
    request,
    project_id: str,
    secret_data: str,
    dir_name: str,
):
    # project_id is a number in some contexts... verify this works
    # the secret really belongs to the nginx-app workload more than the extension
    secret_path = f"projects/{project_id}/secrets/nginx-app-{dir_name}/versions/latest"
    logger.debug("getting config from secret %s", secret_path)
    secretmanager_client = secretmanager.SecretManagerServiceClient()
    secret_version_request = AccessSecretVersionRequest(name=secret_path)
    try:
        secret_payload = secretmanager_client.access_secret_version(
            request=secret_version_request
        ).payload.data.decode("utf-8")
    except PermissionDenied as err:
        logger.warning("failed to decode the secret: %s", err)
        return {}
    except NotFound as err:
        logger.warning("No secret version was found: %s", err)
        return {}
    print(f"setting secret {secret_path} to {secret_data}")


@app.get("/terragrunt-apply-all")
async def terragrunt_apply_all():
    os.chdir(TG_DIR)
    # set env var GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token)
    subprocess.run(
        [
            "terragrunt",
            "run-all",
            "apply",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ],
        check=True,
    )
    return "terragrunt run-all apply ran successfully!"


@app.post("/submit")
async def root_config(
    project_id: str = Form(...),
    remote_state_bucket: str = Form(...),
):
    with open(ROOT_CONFIG_PATH, "w") as fp:
        fp.write(
            hcl.dumps(
                {
                    "locals": {
                        "project_id": project_id,
                        "remote_state_bucket": remote_state_bucket,
                    }
                }
            )
        )
    return "Config saved!"
