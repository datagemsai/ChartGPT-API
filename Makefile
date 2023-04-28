setup: env install kernel

env:
	python3 -m venv venv

install:
	. venv/bin/activate; python -m pip install -r requirements.txt

kernel:
	. venv/bin/activate; python -m ipykernel install --user --name python-***REMOVED***-agi --display-name "Python (***REMOVED*** AGI)"

run:
	. venv/bin/activate; python -m streamlit run app/Intro.py
