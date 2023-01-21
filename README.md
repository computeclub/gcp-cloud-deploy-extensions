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

Expanding on this pattern, notifier authors are encouraged to ship a small terraform
module to stand up all the necessary infra components of a notifier (typically
manages the notifier workload, a PubSub subscription, a service account, and the
required role memberships). This gives an more ideal deployment scenario with
users only needing to build an image and invoke that module to make a deploy
notifier available.

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

1. TODO(brandonjbjelland): Build out a demo that operates against a pipeline targeting a GKE workload
