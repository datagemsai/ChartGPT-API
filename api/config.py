import os

import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(".env")

openai.api_key = os.environ["OPENAI_API_KEY"]

SQL_GPT_MODEL = "gpt-4"
PYTHON_GPT_MODEL = "gpt-4"
GPT_TEMPERATURE = 0.0
