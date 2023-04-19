setup: env install kernel

env:
	python3 -m venv venv

install:
	. venv/bin/activate; python -m pip install -r requirements.txt

kernel:
	. venv/bin/activate; python -m ipykernel install --user --name python-cadlabs-agi --display-name "Python (CADLabs AGI)"

app:
	streamlit run streamlit_app.py
