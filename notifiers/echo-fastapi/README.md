# echo-fastapi

Echo fastapi is a minimal Cloud Deployer called by subscriptions of all cloud
deploy message types and echoing back the details of that message and the
configurations passed to the `execute()` method.

## User story

As an engineer, I want an example notifier demonstrating usage of the python-notifier
library. It would also be useful if this example notifier emitted pubsub
message contents I can better understand the attribute conditions needed to
build other notifiers.

## Configuration schema

`enabled` - a boolean that enables or disables the notifier. If not present the notifier is disabled.

## Developing

1. Install python and pip if necessary. Use `pip` to install `poetry`.

    ```bash
    pip install poetry
    ```

2. Create your virtual env and install all dependencies via `poetry`

    ```bash
    poetry install
    ```

3. Launch the service locally:

    ```bash
    poetry run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
    ```

4. Verify the healthcheck endpoint and send a test payload:

    ```bash
    http localhost:8080
    ```

## Deploying

1. authenticate to GCP:

    ```bash
    # follow URL and paste the secret
    gcloud auth login --update-adc
    # set a terraform recognized env var
    export GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token)
    ```

2. build the deployer container image using cloud build:

    ```bash
    gcloud builds submit \
        --project=${PROJECT_ID} \
        --region=us-central1 \
        --tag us-docker.pkg.dev/${PROJECT_ID}/cloud-deploy-notifiers/echo-fastapi:latest .
    ```

3. deploy all dependent infrastructure using resources in the
`terraform/cloud-deploy-notifier` directory at the repo root. Using the
terragrunt-based demo at the repo root as an example:

    ```bash
    cd demo/terragrunt/echo-fastapi
    terragrunt apply
    ```
