# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Jan 31, 2022

### Added

- Everything. This is the initial repo contents.
- Created 2 new notifiers: `echo-fastapi` demonstrates the basics of how to build a notifier using fastapi. `release-auto-promoter` advances releases by creating rollouts for the next target in a release pipeline when the previous succeeded.
- Extracted a python library to simplify the process of building a notifier.
- Created a terraform module (`terraform/cloud-deploy-notification-infra`) for the notification infrastructure needing to be instantiated once on a project that hosts notifiers.
- Created a terraform module (`terraform/cloud-deploy-notifier`) that can manage all infra components of a typical notifier. Both `echo-fastapi` and `release-auto-promoter` though having slightly different infra requirements, are able to use this module to create all necessary resources.
- The `/demo` directory packs both an example application (`nginx-app`) with its release pipeline IaC and a set of configurations in a `terragrunt` directory. The `terragrunt.hcl` configurations wire together and call the various terraform modules thorughout this repo, showing how all the components relate and can be deployed as separate units.
- `data-samples/` provides 3 example PubSub message payloads so devs can quickly understand the payloads we're working with.
- `.devcontainer` provides configurations for developing this project within a reproducable containerized environment.
