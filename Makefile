setup: env install kernel

env:
	python3 -m venv venv

install:
	. venv/bin/activate; python -m pip install -r requirements.txt

kernel:
	. venv/bin/activate; python -m ipykernel install --user --name python-chartgpt --display-name "Python (ChartGPT)"

run:
	. venv/bin/activate; python -m streamlit run app/ChartGPT.py

test_sample_questions:
	. venv/bin/activate; pytest -n 8 tests/test_sample_questions.py
