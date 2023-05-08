from io import StringIO
from typing import Dict, List, Tuple, Union, Optional
from google.cloud import bigquery
import pandas as pd


class StreamlitDict(dict):
    def __repr__(self):
        import streamlit as st
        df_id = id(self)
        if not df_id in st.session_state:
            st.write(self)
            st.session_state[df_id] = 1
        return dict.__repr__(self)


def get_dataset_ids(client: bigquery.Client) -> List[str]:
    return [dataset.dataset_id for dataset in client.list_datasets()]


def get_table_ids(client: bigquery.Client) -> List[str]:
    dataset_ids = get_dataset_ids(client=client)
    return [table.table_id for dataset_id in dataset_ids for table in client.list_tables(dataset_id)]


def get_tables_summary(
        client: bigquery.Client,
        dataset_ids: Optional[List] = None,
        include_types = False
) -> Dict[str, List[Dict[str, List[Union[Tuple[str, str], str]]]]]:
    if not dataset_ids:
        dataset_ids = get_dataset_ids(client=client)

    tables_summary = StreamlitDict()
    for dataset_id in dataset_ids:
        for table_item in client.list_tables(dataset_id):
            table_id = table_item.table_id
            table_ref = client.dataset(dataset_id).table(table_id)
            table = client.get_table(table_ref)
            if dataset_id not in tables_summary:
                tables_summary[dataset_id] = {}
            tables_summary[dataset_id][table_id] = [
                (schema_field.name, schema_field.field_type) if include_types else schema_field.name
                for schema_field in table.schema
            ]
    return tables_summary

def get_sample_dataframes(
    client: bigquery.Client,
    dataset_id: str,
) -> Dict[str, pd.DataFrame]:
    sample_dfs = {}
    for table_item in client.list_tables(dataset_id):
        table_id = table_item.table_id

        query = f"SELECT * FROM `{client.project}.{dataset_id}.{table_id}` LIMIT 100"
        df = client.query(query).to_dataframe()

        sample_dfs[table_id] = df
    return sample_dfs
