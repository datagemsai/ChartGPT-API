setup: env install kernel

env:
	python3 -m venv venv

install:
	. venv/bin/activate; python -m pip install -r requirements.txt

kernel:
	. venv/bin/activate; python -m ipykernel install --user --name python-chartgpt --display-name "Python (ChartGPT)"

test_sample_questions:
	. venv/bin/activate; pytest -n 8 tests/test_sample_questions.py

format:
	black .
	isort .

# Start web app, API, Discord bot

start_app_staging:
	gcloud config set project chartgpt-staging
	. venv/bin/activate; python -m streamlit run app/Home.py

start_app_production:
	gcloud config set project chartgpt-production
	. venv/bin/activate; python -m streamlit run app/Home.py

start_api:
	. venv/bin/activate; python -m api

start_discord_bot:
	. venv/bin/activate; python -m app.discord_bot

# GCloud setup

gcloud_setup_staging:
	gcloud auth login
	gcloud config set project chartgpt-staging
	gcloud config set run/region europe-west4
	gcloud config set app/cloud_build_timeout 1600
	gcloud artifacts repositories create chartgpt-staging --repository-format=docker \      
		--location=europe-west3 --description="ChartGPT Staging"

gcloud_setup_production:
	gcloud auth login
	gcloud config set project chartgpt-production
	gcloud config set run/region europe-west4
	gcloud config set app/cloud_build_timeout 1600
	gcloud artifacts repositories create chartgpt-production --repository-format=docker \      
		--location=europe-west3 --description="ChartGPT Production"

project_staging:
	gcloud config set project chartgpt-staging
	terraform -chdir=infrastructure workspace select staging

project_production:
	gcloud config set project chartgpt-production
	terraform -chdir=infrastructure workspace select production

# Build
GIT_HASH = $(shell git rev-parse --short HEAD)

build_app_staging: project_staging
	gcloud builds submit --region=europe-west1 --config cloudbuild.yaml --substitutions=_IMAGE_TAG=${GIT_HASH}

build_app_production: project_production
	gcloud builds submit --region=europe-west1 --config cloudbuild.yaml --substitutions=_IMAGE_TAG=${GIT_HASH}

build_caddy_staging: project_staging
	cd infrastructure/caddy/ && gcloud builds submit --region=europe-west1 --config cloudbuild.yaml --substitutions=_IMAGE_TAG=${GIT_HASH}

build_caddy_production: project_production
	cd infrastructure/caddy/ && gcloud builds submit --region=europe-west1 --config cloudbuild.yaml --substitutions=_IMAGE_TAG=${GIT_HASH}

build_api_staging: project_staging
	gcloud builds submit --region=europe-west1 --config api/cloudbuild.yaml --substitutions=_IMAGE_TAG=${GIT_HASH}

build_api_production: project_production
	gcloud builds submit --region=europe-west1 --config api/cloudbuild.yaml --substitutions=_IMAGE_TAG=${GIT_HASH}

build_staging: build_app_staging build_caddy_staging build_api_staging

build_production: build_app_production build_caddy_production build_api_production

# Planning

terraform_plan_staging: project_staging
	terraform -chdir=infrastructure fmt  # formatting
	terraform -chdir=infrastructure init # initializing terraform plugins
	terraform -chdir=infrastructure plan -var-file="variables/staging.tfvars" # checking the plan 

terraform_plan_production: project_production
	terraform -chdir=infrastructure fmt  # formatting
	terraform -chdir=infrastructure init # initializing terraform plugins
	terraform -chdir=infrastructure plan -var-file="variables/production.tfvars"  # checking the plan 

# Deployment

terraform_deploy_staging: project_staging
	terraform -chdir=infrastructure workspace select staging
	terraform -chdir=infrastructure apply --auto-approve -var-file="variables/staging.tfvars"

terraform_deploy_production: project_production
	terraform -chdir=infrastructure workspace select production
	terraform -chdir=infrastructure apply --auto-approve -var-file="variables/production.tfvars"

# deploy_app_production:
# 	gcloud app deploy --project=chartgpt-production app_production.yaml

# deploy_app_staging:
# 	gcloud app deploy --project=chartgpt-staging app_staging.yaml
