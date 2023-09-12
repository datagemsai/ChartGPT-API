import json
import os

from google.cloud import bigquery
from google.oauth2 import service_account

from api import config

scopes = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
]

if config.ENV == "LOCAL":
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GCP_SERVICE_ACCOUNT"], strict=False)
    ).with_scopes(scopes)
    bigquery_client = bigquery.Client(credentials=credentials)
else:
    # If deployed using Google Cloud, use default credentials
    bigquery_client = bigquery.Client()
