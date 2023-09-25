import os

import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

ENV = os.environ.get("ENV", "LOCAL")
PROJECT = os.environ.get("PROJECT", "LOCAL")

SQL_GPT_MODEL = "gpt-4"
PYTHON_GPT_MODEL = "gpt-4"
GPT_TEMPERATURE = 0.0

if ENV != "LOCAL":
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    sentry_sdk.init(
        dsn="https://1d51eab7039610dcf03fc2f96d7fe929@o4505696591544320.ingest.sentry.io/4505883970371584",
        integrations=[FastApiIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )
