

from google.oauth2 import service_account
from google.cloud import bigquery
from .bigquery_pipeline import save_to_bigquery
import json
import gspread
import os
import pandas as pd

schema = [
        bigquery.SchemaField("company_name", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("url", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("city", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("state", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("country", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("employees", bigquery.enums.SqlTypeNames.INTEGER),
        bigquery.SchemaField("linkedin_url", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("founded", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("Industry", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("CityRanking", bigquery.enums.SqlTypeNames.INTEGER),
        bigquery.SchemaField("estimated_revenues", bigquery.enums.SqlTypeNames.FLOAT),
        bigquery.SchemaField("job_openings", bigquery.enums.SqlTypeNames.INTEGER),
        bigquery.SchemaField("keywords", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("LeadInvestors", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("Accelerator", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("btype", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("total_funding", bigquery.enums.SqlTypeNames.FLOAT),
        bigquery.SchemaField("product_url", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("indeed_url", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("growth_percentage", bigquery.enums.SqlTypeNames.FLOAT),
    ]


credentials = service_account.Credentials.from_service_account_info(json.loads(os.environ["gcp_service_account"], strict=False)).with_scopes([
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
])


def clean_funded(df):
    # old_rows = df.shape[0]
    # df = df.loc[df['founded'] != '']
    # print(f"Dropped [{old_rows - df.shape[0]}] rows from removing rows with empty 'founded' values")
    df['founded'] = df['founded'].astype(str)
    return df


def clean_job_openings(df):
    df['job_openings'] = df['job_openings'].replace('', 0).astype(int)
    return df


def clean_valuation(df):
    # df['valuation'] = df['valuation'].replace('', 0).astype(int)
    df = df.drop('valuation', axis=1, errors='ignore')
    return df


def clean_contact_info(df):
    df = df.drop('contact_info', axis=1, errors='ignore')
    return df


def clean_company_name(df):
    old_rows = df.shape[0]
    df['company_name'] = df['company_name'].astype(str)
    df = df.loc[df['company_name'] != '']
    print(f"Dropped [{old_rows - df.shape[0]}] rows from removing rows with empty 'company_name' values")
    return df


def clean_total_funding(df):
    duplicated_column = 'total_funding'
    column_indices = [i for i, name in enumerate(df.columns) if name == duplicated_column]

    # Drop the first occurrence of the duplicated column
    if len(column_indices) > 1:
        df = df.iloc[:, [i for i in range(df.shape[1]) if i != column_indices[0]]]

    specific_string = '#VALUE!'
    df = df[~df[duplicated_column].str.contains(specific_string, na=False)]  # drop rows which contain specific_string
    df['total_funding'] = df['total_funding'].replace('', 0).astype(int)
    return df


def clean_growth_percentage(df):
    df['growth_percentage'] = df['growth_percentage'].replace('', 0.0).astype(float)
    return df


def clean_df(df):
    df = clean_funded(df=df)
    df = clean_job_openings(df=df)
    df = clean_valuation(df=df)
    df = clean_contact_info(df=df)
    df = clean_company_name(df=df)
    df = clean_total_funding(df=df)
    df = clean_growth_percentage(df=df)
    return df


def import_sheet_from_gsheet():
    gc = gspread.authorize(credentials)
    # NB: the account that executes this notebook must have permission to view this spreadsheet
    # NB: this cell will request permission to access your Google Account
    gsheets = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Dq6Hd_oOXSqGZ_11Xm7MnOYm_gNgnyztLa1WEY7-1tA')

    # get_all_values gives a list of rows.
    rows = gsheets.worksheet('Sheet1').get_all_values(value_render_option="UNFORMATTED_VALUE")
    return pd.DataFrame.from_records(rows[1:], columns=rows[0])


def save_sheet_as_csv():
    df = import_sheet_from_gsheet()
    df = clean_df(df=df)

    file_name = 'growjo_fastest_growing_companies'
    file_path = f"analytics_bot_langchain/data/growjo/{file_name}"
    df.to_csv(f'{file_path}.csv', index=False)

    dataframes = {'growjo_fastest_growing_companies': df}

    client = bigquery.Client(credentials=credentials)
    save_to_bigquery(dataframes=dataframes, schema=schema,  dataset_id=file_name, client=client, project_id="psychic-medley-383515", overwrite_existing_table=True)

