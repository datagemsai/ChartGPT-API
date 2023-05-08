setup: env install kernel

env:
	python3 -m venv venv

install:
	. venv/bin/activate; python -m pip install -r requirements.txt

kernel:
	. venv/bin/activate; python -m ipykernel install --user --name python-cadlabs-agi --display-name "Python (CADLabs AGI)"

run:
	. venv/bin/activate; python -m streamlit run app/chartGPT.py

test_sample_questions:
	. venv/bin/activate; pytest -n 8 tests/test_sample_questions.py

gcloud-deploy-production:
	gcloud app deploy gcloud_production.yaml

gcloud-deploy-staging:
	gcloud app deploy gcloud_staging.yaml
