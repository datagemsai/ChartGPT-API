import base64
import re
import uuid
from typing import List, Optional
from cachetools import cached
from cachetools.keys import hashkey
import pandas as pd

from google.cloud import bigquery


def create_type_string(types: List[type]) -> str:
    def get_qualified_name(t):
        return f"{t.__module__}.{t.__name__}"
    
    type_names = [get_qualified_name(t) for t in types]
    
    list_type_str = f"List[Union[{', '.join(type_names)}]]"
    single_type_str = f"Union[{', '.join(type_names)}]"
    
    return f"Union[{list_type_str}, {single_type_str}]"


def convert_period_dtype_to_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    # Convert Period dtype to timestamp to ensure DataFrame is JSON serializable
    return df.astype(
        {
            col: "datetime64[ns]"
            for col in df.columns
            if pd.api.types.is_period_dtype(df[col])
        }
    )


def sort_dataframe(df):
    # Check if the index is a DateTime index
    if isinstance(df.index, pd.DatetimeIndex):
        return df.sort_index()
    
    # Check if any of the columns have date-like values
    for column_name in df.columns:
        column = df[column_name]
        if (
            pd.api.types.is_datetime64_any_dtype(column)
            or pd.api.types.is_period_dtype(column)
            or pd.api.types.is_interval_dtype(column)
            or pd.api.types.is_timedelta64_ns_dtype(column)
        ):
            return df.sort_values(by=column_name)
    
    # If no date column is found, sort by index
    return df.sort_index()


def get_dataframe_summary(df: pd.DataFrame, max_len=10) -> dict[str, str]:
    return {
        column_name: f"{sample[:max_len]}: {dtype}"
        for column_name, sample, dtype in zip(df.columns, df.iloc[0], df.dtypes)
    }


def clean_jupyter_shell_output(output: str, remove_final_result: bool = False) -> str:
    if remove_final_result:
        return re.sub(r'Out\[\d+\]:.*', '', output, flags=re.DOTALL).rstrip()
    else:
        return re.sub(r'Out\[\d+\]:\s*', '', output)


def generate_uuid() -> str:
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8")
    return r_uuid.replace("=", "")


def parse_data_source_url(data_source_url) -> tuple[str, str, str, Optional[str]]:
    # Regular expression pattern
    pattern = r"^(?:([a-z]+)/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)(?:/([a-zA-Z0-9_-]+))?)?$"

    match = re.match(pattern, data_source_url)
    if not match:
        raise ValueError(f"Invalid data source URL format: {data_source_url}")

    # Extracting values from the matched groups
    data_source = match.group(1)
    project = match.group(2)
    collection = match.group(3)
    entity = match.group(4)  # This will be None if not provided

    return data_source, project, collection, entity


# TODO Complete method `check_bigquery_data_exists`
# def check_bigquery_data_exists(client: bigquery.Client, data_source_url: str) -> bool:
#     _data_source, project, dataset_id, table_id = parse_data_source_url(data_source_url)

#     if not project:
#         project = client.project

#     if dataset_id:
#         # Filter bigquery.Dataset objects by dataset_id
#         datasets = [
#             dataset
#             for dataset in list(client.list_datasets(project=project))
#             if dataset.dataset_id == dataset_id
#         ]
#     else:
#         datasets = list(client.list_datasets(project=project))

#     if not datasets:
#         return False

#     if table_id:
#         # Filter bigquery.Table objects by table_id
#         tables = [
#             table
#             for table in list(client.list_tables(datasets[0]))
#             if table.table_id == table_id
#         ]
#     else:
#         tables = list(client.list_tables(datasets[0]))

#     if not tables:
#         return False
#     else:
#         return True

@cached(cache={}, key=lambda client, data_source_url: hashkey(data_source_url))
def get_tables_summary(
    client: bigquery.Client,
    data_source_url: str = "",
) -> str:
    markdown_summary = ""

    if data_source_url:
        _data_source, project, dataset_id, table_id = parse_data_source_url(data_source_url)
    else:
        project = None
        dataset_id = None
        table_id = None

    if not project:
        project = client.project

    if dataset_id:
        # Filter bigquery.Dataset objects by dataset_id
        datasets = [
            dataset
            for dataset in list(client.list_datasets(project))
            if dataset.dataset_id == dataset_id
        ]
    else:
        datasets = list(client.list_datasets(project))

    table_ids = [table_id] if table_id else None

    for dataset in datasets:
        dataset_id = dataset.dataset_id
        markdown_summary += f"## Dataset: {dataset_id}\n"

        # Filter bigquery.Table objects by table_ids
        if table_ids:
            tables = [
                table
                for table in list(client.list_tables(dataset))
                if table.table_id in table_ids
            ]
        else:
            tables = list(client.list_tables(dataset))

        for table in tables:
            table_id = table.table_id
            table_ref = client.dataset(dataset_id, project=project).table(table_id)
            table = client.get_table(table_ref)

            # SQL-like CREATE TABLE statement
            create_table_statement = (
                f"CREATE TABLE `{project}.{dataset_id}.{table_id}` (\n"
            )

            for field in table.schema:
                create_table_statement += f'"{field.name}" {field.field_type}'

                if field.mode == "REQUIRED":
                    create_table_statement += " NOT NULL"

                create_table_statement += ","
                if field.description:
                    create_table_statement += f" - {field.description}"
                create_table_statement += "\n"

            # Here we are not adding primary and foreign keys, but they can be added based on the dataset schema.
            create_table_statement = create_table_statement.rstrip(",\n") + "\n)"

            markdown_summary += f"### {dataset_id}.{table_id}\n"
            markdown_summary += f"```\n{create_table_statement}\n```\n"

    return markdown_summary


def apply_lower_to_where(sql):
    """
    Applies the LOWER function to all string comparisons in the WHERE clause of a SQL query.
    """
    # Regular expression to find the WHERE clause
    where_clause = re.search(r"\bWHERE\b(.*)", str(sql), flags=re.IGNORECASE)

    # If no WHERE clause is found, return the original SQL
    if where_clause is None:
        return sql

    # Extract the WHERE clause
    where_clause = where_clause.group(1)

    # Find all comparisons within the WHERE clause where the value is a string
    comparisons = re.findall(r'(\w+)\s*=\s*([\'"].+?[\'"])', where_clause)

    # Replace each comparison with the LOWER function, only for strings
    for col, value in comparisons:
        old_comparison = f"{col} = {value}"
        new_comparison = f"LOWER({col}) = LOWER({value})"
        where_clause = where_clause.replace(old_comparison, new_comparison, 1)

    # Replace the original WHERE clause with the modified one
    modified_sql = re.sub(
        r"\bWHERE\b.*", f"WHERE{where_clause}", sql, flags=re.IGNORECASE
    )

    return modified_sql
