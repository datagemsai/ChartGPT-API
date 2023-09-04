import re
from typing import List, Optional
from google.cloud import bigquery


def get_tables_summary(
    client: bigquery.Client,
    datasets: List[bigquery.Dataset],
    dataset_ids: Optional[List[str]] = None,
    table_ids: Optional[List[str]] = None,
) -> str:
    markdown_summary = ""

    # Filter bigquery.Dataset objects by dataset_ids
    if dataset_ids:
        datasets = [
            dataset for dataset in datasets if dataset.dataset_id in dataset_ids
        ]

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
            table_ref = client.dataset(dataset_id).table(table_id)
            table = client.get_table(table_ref)

            # SQL-like CREATE TABLE statement
            create_table_statement = f"CREATE TABLE {dataset_id}.{table_id} (\n"

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
    where_clause = re.search(r"\bWHERE\b(.*)", sql, flags=re.IGNORECASE)

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
