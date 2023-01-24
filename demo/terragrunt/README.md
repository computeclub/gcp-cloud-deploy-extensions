# terragrunt examples

This directory contains a minimal example of deploying:

1. nginx-app CI/CD and infra resources.
2. the baseline Cloud Deploy resources found in the root `terraform/` directory
3. the `echo-fastapi` example notifier.

## Cheat code - speed run

Standing up all components is useful for showing everything working together but
less useful for folks wanting a walkthrough. Follow the tutorial series for that
full context walkthrough but jump here to stand up everything at once.

1. configure terragrunt to use a central CI/CD project:

    ```bash
    cp example.config.hcl config.hcl
    # populate relevant values
    code config.hcl
    ```
