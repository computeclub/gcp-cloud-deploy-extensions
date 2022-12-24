# demo/nginx-app

An application repo including dependent infra definitions.

## Build and create a deployment

1. submit a cloud build job to build the container image, push it to the
    registry, and start a Cloud Deploy release:

    ```bash
    gcloud builds submit . \
        --project=${PROJECT_ID} \
        --substitutions=_EPOCH=$(date +%s),_REGISTRY_REPO_URL=us-docker.pkg.dev/${PROJECT_ID}/demo
    ```
