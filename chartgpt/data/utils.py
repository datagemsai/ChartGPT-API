import locale
import re
import pandas as pd
import numpy as np


def format_bigquery_column_names(df):
    # Remove special charachters
    df.columns = [re.sub(r'[^a-zA-Z0-9\s]+', '', column) for column in df.columns]
    # Remove spaces at beginning and end
    df.columns = df.columns.str.strip()
    # Replace spaces with underscore
    df.columns = df.columns.str.replace(' ', '_')
    # Define a function to convert camel-case to kebab-case
    def camel_to_kebab(s):
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
        string = locale.atof(string)
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
        series = series.apply(lambda x: locale.atof(x) if is_locale_string(x) else x)
        series = pd.to_numeric(series)

    return series

def locale_to_float_dataframe(df):
    # Iterate over all columns in the DataFrame
    for column in df.columns:
        df[column] = locale_to_float_series(df[column])
    return df
