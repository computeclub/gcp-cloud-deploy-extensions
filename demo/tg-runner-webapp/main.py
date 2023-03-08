# -*- coding: utf-8 -*-
"""This is an example Cloud Deploy app responder."""
import asyncio
import json
import logging
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

from pathlib import Path
from fastapi import FastAPI, Request, Form, WebSocket
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
DIR_OBJECTS = [f for f in os.scandir(TG_DIR) if f.is_dir() and f.name != ".terraform"]
DIRS_DICT = {f.name: {} for f in DIR_OBJECTS}
SECRETMANAGER_CLIENT = secretmanager.SecretManagerServiceClient()


async def get_secrets(dir_path: str):
    """."""
    initial_dir = os.getcwd()
    os.chdir(dir_path)
    result = subprocess.run(
        [
            "terragrunt",
            "output",
            "-json",
            "secrets",
        ],
        check=True,
        stdout=subprocess.PIPE,
    )
    os.chdir(initial_dir)
    secrets_json = json.loads(result.stdout.decode("utf8"))
    secrets = [s["name"] for s in secrets_json.values()]
    secrets_dict = {}
    for secret in secrets:
        latest_secret_version_path = f"{secret}/versions/latest"
        try:
            secret_version_request = AccessSecretVersionRequest(
                name=latest_secret_version_path,
            )
            secret_payload = json.loads(
                SECRETMANAGER_CLIENT.access_secret_version(
                    request=secret_version_request
                ).payload.data.decode("utf-8")
            )
            secrets_dict[secret] = secret_payload
        except PermissionDenied as err:
            logger.warning("Insufficient permissions to fetch secret: %s", err)
            secrets_dict[secret] = False
        except NotFound as err:
            logger.warning("No secret version was found: %s", err)
            secrets_dict[secret] = False
    return secrets_dict


@app.on_event("startup")
async def fetch_tg_dir_data() -> None:
    """
    .
    """
    for dir_name, dir_data in DIRS_DICT.items():
        if not dir_name.endswith("-app-infra"):
            dir_data["secrets"] = {}
        else:
            dir_data["secrets"] = await get_secrets(
                dir_path=f"{TG_DIR}{os.sep}{dir_name}",
            )

        dir_data["all_secrets_set"] = bool(all(dir_data["secrets"].values()))
        dir_data["secrets_set"] = [bool(s) for s in dir_data["secrets"].values()].count(
            True
        )
        dir_data["secrets_total"] = len(dir_data["secrets"].values())

        if not os.path.isfile(f"{TG_DIR}{os.sep}{dir_name}{os.sep}.tg_state"):
            dir_data["terragrunt_applied"] = False
        else:
            dir_data["terragrunt_applied"] = True


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serves the index."""
    if os.path.isfile(ROOT_CONFIG_PATH):
        with open(ROOT_CONFIG_PATH, "r", encoding="utf8") as fp:
            root_config = hcl.load(fp)
    else:
        root_config = {}
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "dirs_dict": DIRS_DICT,
            "tg_dir": TG_DIR,
            "root_config": root_config,
        },
    )


@app.get("/workspace/{id}", response_class=HTMLResponse)
async def get_workspace_details(request: Request, id: str):
    """."""
    return templates.TemplateResponse(
        "workspace.html",
        {
            "request": request,
            "id": id,
            "dir_details": DIRS_DICT[id],
        },
    )


@app.post("/workspace/{id}/configure")
async def configure_workspace(
    request,
    id: str,
    project_id: str,
    secret_data: str,
    dir_name: str,
):
    """."""
    print(dir_name)


def run_terragrunt_apply_all():
    """."""
    initial_dir = os.getcwd()
    os.chdir(TG_DIR)
    tg_run = subprocess.run(
        [
            "terragrunt",
            "run-all",
            "apply",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ],
        check=True,
    )
    os.chdir(initial_dir)
    return tg_run


@app.get("/terragrunt-apply-all")
async def terragrunt_apply_all():
    """."""
    # set env var GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token)
    logger.info("running terragrunt apply all in a process pool")
    with ProcessPoolExecutor() as executor:
        result = executor.submit(run_terragrunt_apply_all)
    while not result.done():
        logger.info("terragrunt apply all still running...")
        await asyncio.sleep(1)
    logger.info("terragrunt run-all apply ran successfully!")


@app.post("/submit")
async def submit_root_tg_config(
    project_id: str = Form(...),
    remote_state_bucket: str = Form(...),
):
    """."""
    with open(ROOT_CONFIG_PATH, "w", encoding="utf8") as fp:
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


base_dir = Path(__file__).resolve().parent
log_file = "app.log"


async def log_reader(n=5):
    log_lines = []
    with open(f"{base_dir}/{log_file}", "r") as file:
        for line in file.readlines()[-n:]:
            if line.__contains__("ERROR"):
                log_lines.append(f'<span class="text-red-400">{line}</span><br/>')
            elif line.__contains__("WARNING"):
                log_lines.append(f'<span class="text-orange-300">{line}</span><br/>')
            else:
                log_lines.append(f"{line}<br/>")
        return log_lines


@app.websocket("/ws/log")
async def websocket_endpoint_log(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await asyncio.sleep(1)
            logs = await log_reader(30)
            await websocket.send_text(logs)
    except Exception as e:
        print(e)
    finally:
        await websocket.close()
