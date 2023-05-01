from google.cloud import bigquery
from analytics_bot_langchain.data.bigquery_pipeline import clean_csv_files_and_save_to_bigquery, clean_local_csv_files, Datatype
from analytics_bot_langchain.data.dune import execute_query


tables_id = {
        "nft_lending_aggregated_borrow": 1205836,
}


def query_dune_api_and_save_dataset_to_bq(table_name="nft_lending_aggregated_borrow", datatype = Datatype.nftfi):
    clean_csv_files_and_save_to_bigquery(table_name=table_name, datatype=datatype)



