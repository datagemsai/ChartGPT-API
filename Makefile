setup: env install kernel

env:
	python3 -m venv venv

install:
	. venv/bin/activate; python -m pip install -r requirements.txt

kernel:
	. venv/bin/activate; python -m ipykernel install --user --name python-chartgpt --display-name "Python (ChartGPT)"

test_sample_questions:
	. venv/bin/activate; pytest -n 8 tests/test_sample_questions.py

# Start web app, API, Discord bot

start_app:
	. venv/bin/activate; python -m streamlit run app/ChartGPT.py

start_api:
	. venv/bin/activate; python -m api.app

start_discord_bot:
	. venv/bin/activate; python -m app.discord_bot

# Deployment

deploy_app_production:
	gcloud config set project chartgpt-production
	gcloud config set app/cloud_build_timeout 1600
	gcloud app deploy --project=chartgpt-production app_production.yaml

deploy_app_staging:
	gcloud config set project chartgpt-staging
	gcloud config set app/cloud_build_timeout 1600
	gcloud app deploy --project=chartgpt-staging app_staging.yaml
