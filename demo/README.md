# End to end demo

This directory gives an end-to-end demo of:

1. A barebones nginx application deployed to cloud run - imagine this as your app
2. All infra resources needed for CI/CD against that application using Cloud Deploy
3. Examples of integrating with the Cloud Deploy extensions of this repo.

Think of the `/demo` directory as an independent application repo that also
happens to instantiate the project-wide foundational resources needed to use
the Cloud Deploy extensions.
