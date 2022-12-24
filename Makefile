#!make

.PHONY: help
help: ## help using this makefile
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: ## clean the repo of .terraform and .terragrunt-cache dirs
	@ find . -type d -name ".terragrunt-cache" -prune -exec rm -rf {} \; && \
	find . -type d -name ".terraform" -prune -exec rm -rf {} \; &&\
	find . -type f -name ".terraform.lock.hcl" -prune -exec rm {} \; &&\
	echo "✔︎ terragrunt and terraform caches cleared"
