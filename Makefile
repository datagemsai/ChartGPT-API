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
	. venv/bin/activate; python -m app.api

start_discord_bot:
	. venv/bin/activate; python -m app.discord_bot
