from typing import Dict, List
import os
import glob
import pandas as pd
import re
import locale
from locale import atof
import numpy as np
from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st
from pandas.api.types import is_numeric_dtype, is_string_dtype
from enum import Enum
import pprint

pp = pprint.PrettyPrinter(indent=4)

import dotenv

dotenv.load_dotenv()

# Load all CSV files from directory into single BigQuery dataset
import json

credentials = service_account.Credentials.from_service_account_info(json.loads(os.environ["gcp_service_account"], strict=False)).with_scopes([
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
])
client = bigquery.Client(credentials=credentials)


class Datatype(Enum):
    dex = "dex"
    nftfi = "nftfi"


def format_bigquery_column_names(df):
    # Remove special charachters
    df.columns = [re.sub(r'[^a-zA-Z0-9\s]+', '', column) for column in df.columns]
    # Remove spaces at beginning and end
    df.columns = df.columns.str.strip()
    # Replace spaces with underscore
    df.columns = df.columns.str.replace(' ', '_')

    def camel_to_kebab(s):
        """ Define a function to convert camel-case to kebab-case """
        # Replace consecutive capital letters with a single lowercase letter
        s = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', s)
        # Convert remaining camel-case string to kebab-case
        s = re.sub(r'(?<!^)(?<!_)(?=[A-Z])(?![A-Z])', '_', s).lower()
        return s

    # Apply the function to all column names
    df.columns = df.columns.map(camel_to_kebab)
    return df


def clean_nftfi_loan_dataframe(df) -> pd.DataFrame:
    # Convert date from Google datetime to Pandas datetime
    # df["date"] = df["date"].astype('datetime64[s]')
    df["date"] = pd.to_datetime(df['date'], unit='d', origin='1899-12-30')

    # Set precision of Pandas datetime to avoid BigQuery precision error
    df["loan_start_time"] = df["loan_start_time"].astype('datetime64[s]')
    df["loan_due_time"] = df["loan_due_time"].astype('datetime64[s]')

    # Remove invalid values
    # mask = df == "#DIV/0! (Function DIVIDE parameter 2 cannot be zero.)"
    # df[mask] = np.nan
    # df["apr"] = df["apr"].apply(lambda x: x if isinstance(x, float) else np.nan)
    df.replace(r"#DIV/0!", np.nan, regex=True, inplace=True)
    df.replace(r"#N/A", "", regex=True, inplace=True)

    # Clip NFT collateral ID as it has a string value, an integer, that is larger than Python int64 type 
    df["nft_collateral_id"] = df["nft_collateral_id"].astype(float).astype(np.int64)
    df["platform_fee"] = df["platform_fee"].astype(float)

    # Drop repaid and liquidation date as they have invalid values 
    df.drop(["repaid_date", "liquidation_date"], axis=1, inplace=True)
    # df["repaid_date"] = df["repaid_date"].astype('datetime64[s]')
    # df["liquidation_date"] = df["liquidation_date"].astype('datetime64[s]')

    # Drop last column as it is unnamed
    df = df.drop('', axis=1, errors='ignore')
    return df


def is_percentage_string(s):
    return isinstance(s, str) and ("%" in s)


def is_locale_string(s):
    return isinstance(s, str) and ("," in s or "." in s) and s.replace(',', '').replace('.', '').isnumeric()


def locale_to_float(string):
    if is_locale_string(string):
        if ',' in string:
            locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # French locale, using comma as decimal separator
        else:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # US locale, using dot as decimal separator        
        string = atof(string)
    return string


def locale_to_float_series(series):
    # Check if the column contains locale strings
    contains_locale_strings = any(series.apply(is_locale_string))

    if contains_locale_strings:
        # Identify locale by checking the first non-null value
        first_non_null = series.dropna().iloc[0]

        # Check if the first non-null value contains a comma as a decimal separator
        if ',' in first_non_null:
            locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # French locale, using comma as decimal separator
        else:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # US locale, using dot as decimal separator

        # Convert strings with locale info to floats
        series = series.apply(lambda x: atof(x) if is_locale_string(x) else x)
        series = pd.to_numeric(series)

    return series


def locale_to_float_dataframe(df):
    # Iterate over all columns in the DataFrame
    for column in df.columns:
        df[column] = locale_to_float_series(df[column])
    return df


def clean_nans(df: pd.DataFrame) -> pd.DataFrame:
    df_cleaned = df.copy()
    for column in df.columns:
        if df[column].isna().any():
            print(f"Column {column} contains NaN values.")

            # Drop the rows containing NaN values in column
            df_cleaned = df_cleaned.dropna(subset=[column])

            print(f"\nOriginal DataFrame length: {df.shape[0]}")
            print(f"\nDataFrame after dropping rows with NaN values in column {column}: {df_cleaned.shape[0]}")
    return df_cleaned


def fill_if_entirely_nans(df: pd.DataFrame) -> pd.DataFrame:
    # Iterate through the columns and check if the entire column contains NaN values
    for column in df.columns:
        if df[column].isna().all():
            print(f"Column {column} contains only NaN values.")

            # Check the data type of the column and replace NaN values accordingly
            if is_numeric_dtype(df[column]):
                df[column] = df[column].fillna(0)
            elif is_string_dtype(df[column]):
                df[column] = df[column].fillna('')
    return df


def drop_if_entirely_nans(df: pd.DataFrame) -> pd.DataFrame:
    # Iterate through the columns and check if the entire column contains NaN values
    for column in df.columns:
        if df[column].isna().all():
            print(f"Column {column} contains only NaN values.")

            # Drop the column containing only NaN values
            df.drop(column, axis=1, inplace=True)
    return df


def set_datatype(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        # Check for string type
        if any(isinstance(val, str) for val in df[column]):
            df[column] = df[column].astype(str)
        # Check for float type
        elif any(isinstance(val, float) and not isinstance(val, int) for val in df[column]):
            df[column] = df[column].astype(float)
        # Check for integer type
        elif all(isinstance(val, int) for val in df[column]):
            df[column] = df[column].astype(int)
    return df


def clean_local_csv_files(datatype: Datatype, table_name: str, dune_query: bool):
    dataframes = {}
    csv_file_directory = f"analytics_bot_langchain/data/dune/{datatype.value}/"
    if dune_query:
        files = [csv_file_directory + table_name + '.csv']
    else:
        files = glob.glob(os.path.join(csv_file_directory, "*.csv"))
    for csv_file_path in files:
        # Get the file name from the file path
        file_name = os.path.basename(csv_file_path)
        # Remove the file extension
        file_name = os.path.splitext(file_name)[0]

        # Load the CSV file into a pandas DataFrame
        df = (
            pd.read_csv(
                csv_file_path,
                dtype=str,
                usecols=lambda column: not column.startswith("Unnamed"),
                encoding='utf-8',
                engine='python',
                on_bad_lines='warn'
            )
        )

        df = drop_if_entirely_nans(df=df)
        df = clean_nans(df=df)
        df = set_datatype(df=df)
        if datatype == datatype.dex:
            df['token_bought_amount_raw'] = df['token_bought_amount_raw'].astype(str)
            df['token_sold_amount_raw'] = df['token_sold_amount_raw'].astype(str)
            df['block_time'] = pd.to_datetime(df['block_time'], format='%Y-%m-%d %H:%M:%S.%f %Z', utc=True)
            df['block_date'] = pd.to_datetime(df['block_date'], format='%Y-%m-%d %H:%M:%S.%f %Z', utc=True)
            df = df[df['blockchain'] != 'fantom']
        elif datatype == datatype.nftfi:
            for col in df.columns:
                if col == 'dt':
                    continue
                if 'repay' in table_name:
                    df[col] = df[col].astype(float)
                elif 'borrow' in table_name:
                    df[col] = df[col].astype(int)
                elif 'users' in table_name:
                    df[col] = df[col].astype(int)
                elif 'liq' in table_name:
                    df[col] = df[col].astype(int)
                elif 'nft_collection' in table_name:
                    df['num_nft_as_collateral'] = df['num_nft_as_collateral'].astype(int)
                    df['borrow_usd'] = df['borrow_usd'].astype(float)
                    df['num_unique_nft'] = df['num_unique_nft'].astype(int)
                    df['ranking'] = df['ranking'].astype(int)
                    break
                else:
                    raise Exception(f'unspecified datatype for {table_name}')
            if 'collection' not in table_name:
                df['dt'] = pd.to_datetime(df['dt'], format='%Y-%m-%d %H:%M')

        if "nftfi_loan_data" in file_name:  # format_bigquery_column_names(df)
            clean_nftfi_loan_dataframe(df)

        df = locale_to_float_dataframe(df)  # Convert locale strings to float
        dataframes[file_name] = df
    return dataframes


def save_to_bigquery(dataframes: Dict, schema: List[bigquery.SchemaField],  dataset_id: str, client=client, project_id="psychic-medley-383515", overwrite_existing_table=False):
    for df_name, df in dataframes.items():

        df_name = df_name.replace(':', '_')
        table_ref = client.dataset(dataset_id, project=project_id).table(df_name)  # Construct a reference to the table

        # Upload the data to BigQuery
        if overwrite_existing_table:
            # Create a LoadJobConfig with WRITE_TRUNCATE to replace the existing table
            job_config = bigquery.LoadJobConfig(
                schema=schema,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                autodetect=True
            )
        else:
            job_config = bigquery.LoadJobConfig(
                schema=schema,
                write_disposition=bigquery.WriteDisposition.WRITE_EMPTY,
                autodetect=True
            )

        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete

        print(f"Loaded {job.output_rows} rows into {dataset_id}.{df_name}.")


def get_schema(table_name='nft_lending_aggregated_borrow'):
    if table_name == 'nft_lending_aggregated_borrow':
        return [
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
    elif table_name == 'nft_lending_liquidate':
        return [
            bigquery.SchemaField(f"dt", bigquery.enums.SqlTypeNames.TIMESTAMP),
            bigquery.SchemaField(f"bend_num_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"nftfi_num_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"pine_num_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"arcade_num_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"jpegd_num_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"drops_num_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"x2y2_num_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"total_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"bend_cumu_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"nftfi_cumu_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"pine_cumu_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"arcade_cumu_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"jpegd_cumu_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"drops_cumu_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"x2y2_cumu_nft_liq", bigquery.enums.SqlTypeNames.INTEGER),
        ]
    elif table_name == 'nft_lending_aggregated_repay':
        return [
            bigquery.SchemaField(f"dt", bigquery.enums.SqlTypeNames.TIMESTAMP),
            bigquery.SchemaField(f"bend_repay_volume", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"nftfi_repay_volume", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"pine_repay_volume", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"arcade_repay_volume", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"jpegd_repay_volume", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"drops_repay_volume", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"x2y2_repay_volume", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"paraspace_repay_volume", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"total_repay_volume", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"cumu_repay_volume_bend", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"cumu_repay_volume_nftfi", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"cumu_repay_volume_pine", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"cumu_repay_volume_arcade", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"cumu_repay_volume_jpegd", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"cumu_repay_volume_drops", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"cumu_repay_volume_x2y2", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"cumu_repay_volume_paraspace", bigquery.enums.SqlTypeNames.FLOAT64),
        ]
    elif table_name == 'nft_lending_aggregated_repay':
        return [
            bigquery.SchemaField(f"dt", bigquery.enums.SqlTypeNames.TIMESTAMP),
            bigquery.SchemaField(f"bend_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"nftfi_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"pine_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"arcade_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"jpegd_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"drops_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"x2y2_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"paraspace_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"total_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"cumu_bend_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"cumu_nftfi_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"cumu_pine_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"cumu_arcade_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"cumu_jpegd_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"cumu_drops_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"cumu_x2y2_users", bigquery.enums.SqlTypeNames.INTEGER),
            bigquery.SchemaField(f"cumu_paraspace_users", bigquery.enums.SqlTypeNames.INTEGER),
        ]
    elif table_name == 'nft_lending_aggregated_nft_collection':
        return [
            bigquery.SchemaField(f"num_nft_as_collateral", bigquery.enums.SqlTypeNames.INT64),
            bigquery.SchemaField(f"borrow_usd", bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField(f"num_unique_nft", bigquery.enums.SqlTypeNames.INT64),
            bigquery.SchemaField(f"nft_collection", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField(f"platform", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField(f"ranking", bigquery.enums.SqlTypeNames.INT64),
        ]
    elif table_name == 'dex':
        # Return the Dune dex schema
        return [
            bigquery.SchemaField("blockchain", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("project", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("version", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("block_date", bigquery.enums.SqlTypeNames.TIMESTAMP),
            bigquery.SchemaField("block_time", bigquery.enums.SqlTypeNames.TIMESTAMP),
            bigquery.SchemaField("token_bought_symbol", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("token_sold_symbol", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("token_pair", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("token_bought_amount", bigquery.enums.SqlTypeNames.FLOAT),
            bigquery.SchemaField("token_sold_amount", bigquery.enums.SqlTypeNames.FLOAT),
            bigquery.SchemaField("token_bought_amount_raw", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("token_sold_amount_raw", bigquery.enums.SqlTypeNames.STRING),
            # bigquery.SchemaField("amount_usd", bigquery.enums.SqlTypeNames.FLOAT),  # EMPTY IN DUNE hence cleaned away
            bigquery.SchemaField("token_bought_address", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("token_sold_address", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("taker", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("maker", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("project_contract_address", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("tx_hash", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("tx_from", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("tx_to", bigquery.enums.SqlTypeNames.STRING),
            # bigquery.SchemaField("trace_address", bigquery.enums.SqlTypeNames.STRING),  # EMPTY IN DUNE hence cleaned away
            bigquery.SchemaField("evt_index", bigquery.enums.SqlTypeNames.STRING),  # INTEGER
        ]


def clean_csv_files_and_save_to_bigquery(table_name: str, datatype: Datatype, dune_query: bool, overwrite_existing_table=True):
    dataframes = clean_local_csv_files(datatype=datatype, table_name=table_name, dune_query=dune_query)
    schema = get_schema(table_name=table_name)
    if datatype == Datatype.nftfi:
        dataset_id = table_name
    elif datatype == Datatype.dex:
        dataset_id = 'dex'
    else:
        raise Exception(f"Unrecognized datatype {datatype}, cannot match it with BQ dataset")
    save_to_bigquery(dataframes=dataframes, overwrite_existing_table=overwrite_existing_table, schema=schema, dataset_id=dataset_id)
