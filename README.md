# GCP Cloud Deploy Extensions

A collection of images and infra to take actions in response to GCP Cloud Deploy
state transitions.

Similar to the collection of cloud builders at
[cloud-builders-community](https://github.com/GoogleCloudPlatform/cloud-builders-community)
and notifiers at
[cloud-build-notifiers](https://github.com/GoogleCloudPlatform/cloud-build-notifiers),
this repo aims to be a commons of utilities to enhance
[Google Cloud Deploy](https://cloud.google.com/deploy/docs/overview). Google
Cloud Deploy provides essential primitives, a useful UI, and granular permissions
for managing releases that can span many environments in Google Cloud. Cloud
Deploy is also very recently GA and lacks some features and functionality of
established CI/CD tools (notifications, conditional release promotion,
auto-rollback on verification failure, post-deploy image tagging, etc.). Instead
gives an interface via [PubSub notifications](https://cloud.google.com/deploy/docs/subscribe-deploy-extensions)
to fill the gaps. The extension solutions here stand up infrastructure and
services necessary to build on top of Cloud Deploy lifecycle events.

## Architecture

The services under `extensions/` follow a similar deployment pattern to those
found in cloud-builders-community and cloud-build-notifiers. Namely, source code,
dockerfiles, and cloudbuild configurations are packaged for users to build, store,
and deploy container images to their GCP projects.

Expanding on this pattern, to manage extension infra, authors should either:

1. verify the `terraform/cloud-deploy-extension` terraform root module is
sufficient to manage all dependent infra for the extension or
2. build a small terraform root module, that likely calls `terraform/cloud-deploy-extension`
as a component module to manage all dependent infra.

In either case, including an example of the variable inputs in an `example.tfvars`
file is a simple way to guide users on how to easily stand up infra.

## Per-pipeline extension configuration

Once deployed, extensions are configured via configuration attached to workload
Deploy Pipelines. Workloads use an extension on an opt-in basis. Following a
kubernetes-like configuration approach, each extension has a distinct
configuration annotation key that Cloud Deploy Pipelines must include if they
want to leverage a extension.

The annotation value should point to a user-configured secret in Secret Manager.
This secret contains configuration values that the extension unpacks during
execution. This is a powerful pattern for a few reasons:

1. It's secure - some extensions will require secret data, others won't necessarily, but it's a good practice to treat all configuration as potentially sensitive and RBAC controlled.
2. Extensions can be liberally deployed without affecting existing pipelines - enabling a extension requires an annotation for opting-in deployment pipelines and the configuration in secret manager.
3. Configuration can be as expressive as you need - Secret manager secret versions can be large (up to 64K) and the standard utf-8 charset is supported.

## Deploy extension index

* [echo-fastapi](extensions/echo-fastapi/) is an example deploy extension in Python
that echos the payload, the configuration secret contents, and kwargs.
* [release-auto-promoter](extensions/release-auto-promoter/) is a extension that
promotes releases as rollouts in deploy pipeline succeed. This reduces a manual
task from release managers or engineers who just want successful deployments to
be promoted to higher envs.
* [image-tagger](extensions/image-tagger/) is a extension that tags container
images that have been successfully deployed. The tags are flexible and based on
templates stored within the extension's configuration and target annotations.

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

## What's upcoming?

1. Build out a demo that operates against a pipeline targeting a GKE workload
2. create an example extension in go
3. build a second go extension, extract an interface
4. blog posts discussing the nuts and bolts of the project
