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

    # def query(
    #     self,
    #     *args,
    #     **kwargs,
    # ) -> bigquery.job.QueryJob:
    #     job = super().query(*args, **kwargs)
    #     job.result()
    #     print(f"BigQuery query {job.query} with {job.total_bytes_billed} bytes billed")
    #     return job

    def list_datasets(self, project=None, **kwargs):
        # Call the original method
        original_datasets = super().list_datasets(project=project, **kwargs)

        # Filter based on allowed datasets
        if self.allowed_datasets is None:
            filtered_datasets = original_datasets
        else:
            filtered_datasets = [
                dataset
                for dataset in original_datasets
                if dataset.dataset_id in self.allowed_datasets
            ]

        return filtered_datasets

    def list_tables(self, dataset, **kwargs):
        # Call the original method
        original_tables = super().list_tables(dataset, **kwargs)

        # Filter based on allowed tables
        if self.allowed_tables is None:
            filtered_tables = original_tables
        else:
            filtered_tables = [
                table
                for table in original_tables
                if table.table_id in self.allowed_tables
            ]

        return filtered_tables


def maxium_usd_to_maximum_bytes_billed(usd: float) -> int:
    usd_per_tib = 6.25
    tib_used_limit = usd / usd_per_tib
    bytes_per_tib = 1.1e12
    bytes_used_limit = tib_used_limit * bytes_per_tib
    return int(bytes_used_limit)


MAX_USD_COST = 2


if config.ENV == "LOCAL":
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GCP_SERVICE_ACCOUNT"], strict=False)
    ).with_scopes(scopes)
    bigquery_client = CustomBigQueryClient(
        credentials=credentials,
        default_query_job_config=bigquery.QueryJobConfig(
            maximum_bytes_billed=maxium_usd_to_maximum_bytes_billed(MAX_USD_COST),
        ),
    )
else:
    # If deployed using Google Cloud, use default credentials
    bigquery_client = CustomBigQueryClient(
        default_query_job_config=bigquery.QueryJobConfig(
            maximum_bytes_billed=maxium_usd_to_maximum_bytes_billed(MAX_USD_COST),
        )
    )
