import inspect
from io import StringIO
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import InternalServerError

from app.config.datasets import Dataset
from app import logger


class StreamlitDict(dict):
    def __repr__(self):
        import streamlit as st

        df_id = id(self)
        if not df_id in st.session_state:
            st.session_state["container"].dataframe(self)
            st.session_state["text"] = "\n\n"
            st.session_state["empty_container"] = st.session_state["container"].empty()
            st.session_state[df_id] = 1
            st.write(self)
            st.session_state[df_id] = 1
        return dict.__repr__(self)


def get_dataset_ids(client: bigquery.Client) -> List[str]:
    return [dataset.dataset_id for dataset in client.list_datasets()]


def get_table_ids(client: bigquery.Client) -> List[str]:
    dataset_ids = get_dataset_ids(client=client)
    return [
        table.table_id
        for dataset_id in dataset_ids
        for table in client.list_tables(dataset_id)
    ]


def get_tables_summary(
    client: bigquery.Client, datasets: List[Dataset], include_types=False
) -> Dict[str, List[Dict[str, List[Union[Tuple[str, str], str]]]]]:
    # Generate tables_summary for all tables in datasets
    tables_summary = StreamlitDict()
    for dataset in datasets:
        dataset_id = dataset.id
        project = dataset.project
        tables_summary[dataset_id] = {}
        for table_id in dataset.tables:
            table_ref = client.dataset(dataset_id, project=project).table(table_id)
            table = client.get_table(table_ref)
            tables_summary[dataset_id][table_id] = [
                (
                    schema_field.name,
                    schema_field.field_type,
                    "Description: "
                    + dataset.column_descriptions.get(schema_field.name, ""),
                )
                if include_types
                else (
                    schema_field.name,
                    "Description: "
                    + dataset.column_descriptions.get(schema_field.name, ""),
                )
                for schema_field in table.schema
            ]
    return tables_summary


def get_example_query(
    datasets: List[Dataset],
) -> str:
    # Generate example_query for all tables in datasets
    example_query = ""
    for dataset in datasets:
        for table_id in dataset.tables:
            example_query += inspect.cleandoc(
                f"""
            SELECT * FROM `{dataset.project}.{dataset.id}.{table_id}` LIMIT 100
            """
            )
    return example_query


def get_sample_dataframes(
    client: bigquery.Client,
    dataset: Dataset,
) -> Dict[str, pd.DataFrame]:
    # Generate sample_dfs for all tables in dataset
    sample_dfs = {}
    for table_id in dataset.tables:
        try:
            query = f"SELECT * FROM `{dataset.project}.{dataset.id}.{table_id}` LIMIT 100"
            df = client.query(query).to_dataframe()
            sample_dfs[table_id] = df
        except InternalServerError:
            logger.exception("BigQuery InternalServerError for query %s", query)
            sample_dfs[table_id] = pd.DataFrame()
    return sample_dfs
