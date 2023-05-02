
from analytics_bot_langchain.data.bigquery_pipeline import clean_csv_files_and_save_to_bigquery, Datatype
from analytics_bot_langchain.data.dune.execute_query import run_query

tables_id = {
        "nft_lending_aggregated_borrow": 1205836,
        "nft_lending_aggregated_repay": 1227068,
        "nft_lending_aggregated_users": 1227127,
        "nft_lending_aggregated_nft_collection": 1227168,
        "nft_lending_liquidate": 1241427,
        "dex": 2421110,
}


def query_dune_api_and_save_dataset_to_bq(table_name: str, query_id: int, datatype: Datatype, dune_query: bool):
    if dune_query:
        # if we query dune API, we save .csv locally and only upload that table to BQ. else we upload all tables in data/dune/nftfi/*.csv to BQ
        run_query(file_name=table_name, datatype=datatype, query_id=query_id)
    clean_csv_files_and_save_to_bigquery(table_name=table_name, datatype=datatype, dune_query=dune_query)


# table_name = "nft_lending_aggregated_repay"
# datatype = Datatype.nftfi

# table_name = "dex"
# datatype = Datatype.dex

table_name = "nft_lending_aggregated_users"
datatype = Datatype.nftfi

# table_name = "nft_lending_liquidate"
# datatype = Datatype.nftfi

# table_name = "nft_lending_aggregated_nft_collection"
# datatype = Datatype.nftfi

# table_name = "nft_lending_aggregated_borrow"
# datatype = Datatype.nftfi
for table in tables_id.keys():
    query_dune_api_and_save_dataset_to_bq(table_name=table, query_id=tables_id[table], datatype=datatype, dune_query=True)


