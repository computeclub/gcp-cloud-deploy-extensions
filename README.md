# GCP Cloud Deploy Notifiers

A collection of images and infra to take actions in response to GCP Cloud Deploy
state transitions.

Similar to the collection of cloud builders at
[cloud-builders-community](https://github.com/GoogleCloudPlatform/cloud-builders-community)
and [cloud-build-notifiers](https://github.com/GoogleCloudPlatform/cloud-build-notifiers),
this repo aims to be a commons of utilities to enhance
[Google Cloud Deploy](https://cloud.google.com/deploy/docs/overview). Google
Cloud Deploy provides essential primitives, a useful UI, and granular permissions
for managing deployments that can span many environments in Google Cloud. Cloud
Deploy also lacks some features and functionality of established CI/CD tools
(notifications, automatic release promotion, auto-rollback on verification failure,
post-deploy image tagging, etc.) but instead gives extension points via
[PubSub notifications](https://cloud.google.com/deploy/docs/subscribe-deploy-notifications)
to flexibly fill these gaps. The solutions here stand up infrastructure and
services necessary to build on top of that notification platform.

## Architecture

The notifier recipes here follow a very similar deployment pattern to the solutions
in cloud-builders-community and cloud-build-notifiers. Namely, source code,
dockerfiles, and cloudbuild configurations are packaged for users to build, store,
and deploy container images to their GCP projects.

Expanding on this pattern, to manage notifier infra, authors should either:

1. verify the `terraform/cloud-deploy-notifier` root module is sufficient to
manage all dependent infra for the notifier or
2. build a small terraform module, that likely calls `terraform/cloud-deploy-notifier`
to manage all dependent infra.

In either case, including an example of the variable inputs in an `example.tfvars`
file is a simple way to guide notifier consumers on how to run this terraform.

## Notifier configuration per pipeline

The way notifiers are configured for usage by workload deploy pipelines differs
to the cloud-build repos. Following a kubernetes-style configuration approach,
once a deploy notifier is deployed, it can operate against notifications
originating from any Cloud Deploy pipeline but until a deploy pipeline opts-in,
a notifier should do nothing.

A workload's deploy pipeline opts-in to using a given notifier via an annotation
on the pipeline (and potentially annotations on targets). The annotation value
should point to a secret in secret manager that the notifier can use for
configuration values during an invocation. This pattern allows any number of
notifiers to be deployed and available to workload pipelines while giving
pipeline owners a simple mechanism to enable and configure a custom set of
notifiers on their pipelines.

## Deploy notifier index

* [echo-fastapi](notifiers/echo-fastapi/) - an example deploy notifier in Python
that echos the payload.
* echo-go - an example deploy notifier in go.

## Development

This repo includes a `.devcontainer` directory so users are able to quickly get
started developing inside a pre-packaged dev environment in VSCode. Read
more about devcontainers [here](https://code.visualstudio.com/docs/devcontainers/containers).

When working in a devcontainer, if you're doing any work against GCP you'll need
to establish GCP credentials. Do this via:

```bash
gcloud auth login --update-adc
```

You'll be prompted to open a browser and paste back an auth code. Afterward, set
an environment variable which many/most/maybe all Google Cloud SDKs support:

```bash
export GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token)
```

## What's forthcoming?

1. Build out a demo that operates against a pipeline targeting a GKE workload
2. create an example notifier in go
3. build a second go notifier, extract an interface
4. blog posts discussing the nuts and bolts of the project
