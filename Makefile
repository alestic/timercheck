
SHELL=/bin/bash
VIRTUALENV=.virtualenv
STAGE=dev

help: ## Show help text
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

$(VIRTUALENV)/bin/activate:
	virtualenv --python $$(which python3.6) $(VIRTUALENV)
	source $(VIRTUALENV)/bin/activate; \
	pip install chalice boto3

virtualenv:: $(VIRTUALENV)/bin/activate

setup:: ## Install prerequisites and virtualenv
	sudo apt-get install python3.6
	sudo -H pip3 install virtualenv

setup:: virtualenv

deploy:: virtualenv ## Deploy to AWS
	source $(VIRTUALENV)/bin/activate; \
	chalice deploy --no-autogen-policy --stage $(STAGE)

local:: ## Run on local port
	source $(VIRTUALENV)/bin/activate; \
	chalice local

logs:: ## Show AWS Lamda function logs
	source $(VIRTUALENV)/bin/activate; \
	chalice logs --include-lambda-messages --stage $(STAGE)

clean:: ## Cleanup local directory
	rm -rf $(VIRTUALENV) __pycache__ .chalice/{venv,deployments,deployed.json}
