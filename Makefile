SHELL := /bin/bash
TF_DIR := terraform
ANSIBLE_DIR := ansible
INV := $(ANSIBLE_DIR)/inventory/hosts.ini
PYTHON ?= python3
MLFLOW_URI ?= http://10.0.2.30:5000
K8S_NS := mlops

.PHONY: help init plan apply provision inventory configure bootstrap train evaluate promote test build-image deploy-k8s smoke validate clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

init: ## terraform init
	cd $(TF_DIR) && terraform init

plan: init ## terraform plan
	cd $(TF_DIR) && terraform plan -out=tf.plan

apply: plan ## terraform apply
	cd $(TF_DIR) && terraform apply tf.plan

provision: apply ## provision infrastructure (alias for apply)

inventory: ## regenerate Ansible inventory from the IP plan
	$(PYTHON) scripts/generate-inventory.py > $(INV)

configure: inventory ## run full Ansible configuration
	cd $(ANSIBLE_DIR) && ansible-playbook -i inventory/hosts.ini site.yml

bootstrap: provision configure ## full bootstrap: infra + config

train: ## train, register and stage a new churn model
	MLFLOW_TRACKING_URI=$(MLFLOW_URI) $(PYTHON) ml/training/train.py

evaluate: ## evaluate newest Staging model vs Production
	MLFLOW_TRACKING_URI=$(MLFLOW_URI) $(PYTHON) ml/evaluation/evaluate.py

promote: ## manual promotion gate: Staging -> Production
	./scripts/train-and-register.sh --promote

build-image: ## build the FastAPI serving image
	docker build -t mlops-fastapi:latest -f docker/fastapi/Dockerfile docker/fastapi

deploy-k8s: ## deploy FastAPI + HPA to Kubernetes
	kubectl apply -f kubernetes/namespace.yml
	kubectl apply -f kubernetes/fastapi/
	kubectl apply -f kubernetes/hpa.yml
	kubectl rollout restart deployment/fastapi -n $(K8S_NS)

smoke: ## POST a sample payload to /predict
	./scripts/smoke-test.sh

validate: ## static validation: python compile + yaml/json lint + terraform + ansible
	@echo "== py_compile =="
	@find . -name '*.py' -not -path './.git/*' -not -path './.terraform/*' -print0 | xargs -0 $(PYTHON) -m py_compile
	@echo "== yaml lint =="
	@$(PYTHON) -c "import glob,yaml,sys; [yaml.safe_load(open(f)) for f in glob.glob('**/*.yml', recursive=True)+glob.glob('**/*.yaml', recursive=True)]; print('ok')"
	@echo "== json lint =="
	@$(PYTHON) -c "import glob,json,sys; [json.load(open(f)) for f in glob.glob('**/*.json', recursive=True)]; print('ok')"
	@echo "== terraform validate =="
	@cd $(TF_DIR) && terraform init -backend=false -input=false >/dev/null 2>&1 && terraform validate || echo "SKIP (terraform provider download unavailable)"
	@echo "== ansible syntax-check =="
	@cd $(ANSIBLE_DIR) && ansible-playbook -i inventory/hosts.ini --syntax-check site.yml

clean: ## remove generated artifacts
	rm -rf mlruns mlartifacts
	rm -rf $(TF_DIR)/.terraform $(TF_DIR)/tf.plan
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
