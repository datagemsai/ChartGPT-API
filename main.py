from google.cloud import bigquery
from analytics_bot_langchain.data.bigquery_pipeline import clean_csv_files_and_save_to_bigquery, clean_local_csv_files, Datatype
from analytics_bot_langchain.data.dune import execute_query

file_name = "nft_lending_aggregated_borrow"
tables_id = {
    "nft_lending_aggregated_borrow": 1205836,
}

datatype = Datatype.nftfi

schema = [
    bigquery.SchemaField(f"dt", bigquery.enums.SqlTypeNames.TIMESTAMP),
    bigquery.SchemaField(f"bend_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"nftfi_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"pine_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"arcade_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"jpegd_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"drops_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"x2y2_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"paraspace_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"total_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"bend_cumu_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"nftfi_cumu_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"pine_cumu_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"arcade_cumu_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"jpegd_cumu_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"drops_cumu_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"x2y2_cumu_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),
    bigquery.SchemaField(f"paraspace_cumu_borrow_volume", bigquery.enums.SqlTypeNames.INTEGER),

]

clean_csv_files_and_save_to_bigquery(schema=schema, datatype=datatype)



