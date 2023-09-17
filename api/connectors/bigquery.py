import json
import os

from google.cloud import bigquery
from google.oauth2 import service_account

from api import config

scopes = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
]


class CustomBigQueryClient(bigquery.Client):
    # Define the allowed datasets and tables as class variables
    allowed_datasets = None
    allowed_tables = None

    def list_datasets(self, project=None, **kwargs):
        # Call the original method
        original_datasets = super().list_datasets(project=project, **kwargs)
        
        # Filter based on allowed datasets
        if self.allowed_datasets is None:
            filtered_datasets = original_datasets
        else:
            filtered_datasets = [dataset for dataset in original_datasets if dataset.dataset_id in self.allowed_datasets]
        
        return filtered_datasets

    def list_tables(self, dataset, **kwargs):
        # Call the original method
        original_tables = super().list_tables(dataset, **kwargs)
        
        # Filter based on allowed tables
        if self.allowed_tables is None:
            filtered_tables = original_tables
        else:
            filtered_tables = [table for table in original_tables if table.table_id in self.allowed_tables]
        
        return filtered_tables


if config.ENV == "LOCAL":
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GCP_SERVICE_ACCOUNT"], strict=False)
    ).with_scopes(scopes)
    bigquery_client = CustomBigQueryClient(credentials=credentials)
else:
    # If deployed using Google Cloud, use default credentials
    bigquery_client = CustomBigQueryClient()
