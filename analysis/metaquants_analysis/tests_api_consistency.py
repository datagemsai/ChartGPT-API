# %%
import pandas as pd
import unittest
from pandas.testing import assert_frame_equal
import re
import numpy as np

# pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth', None)  # Displays all the text for each value in a column
# pd.set_option('display.float_format', '{:,.2f}'.format)


def load_nftfi_table():
    def format_bigquery_column_names(nftfi):
        # Remove special charachters
        nftfi.columns = [re.sub(r'[^a-zA-Z0-9\s]+', '', column) for column in nftfi.columns]
        # Remove spaces at beginning and end
        nftfi.columns = nftfi.columns.str.strip()
        # Replace spaces with underscore
        nftfi.columns = nftfi.columns.str.replace(' ', '_')

        # Define a function to convert camel-case to kebab-case
        def camel_to_kebab(s):
            # Replace consecutive capital letters with a single lowercase letter
            s = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', s)
            # Convert remaining camel-case string to kebab-case
            s = re.sub(r'(?<!^)(?<!_)(?=[A-Z])(?![A-Z])', '_', s).lower()
            return s

        # Apply the function to all column names
        nftfi.columns = nftfi.columns.map(camel_to_kebab)
        return nftfi
    try:
        nftfi = pd.read_csv('loans_raw_loan_input_data.csv')
    except FileNotFoundError:
        nftfi = pd.read_csv('analysis/metaquants_analysis/loans_raw_loan_input_data.csv')
    nftfi = format_bigquery_column_names(nftfi)
    nftfi = nftfi.rename(columns={'loan_id': 'loan_no', 'loan_date': 'date'})

    # Drop nftfi gas price related columns
    for col in nftfi.columns:
        if 'gas' in col:
            nftfi = nftfi.drop(columns=[col], axis=1)
        if 'fee' in col:
            nftfi = nftfi.drop(columns=[col], axis=1)

    nftfi['loan_no_cleaned'] = nftfi['loan_no'].str.split('-').apply(lambda x: x[-1])
    nftfi['date'] = pd.to_datetime(nftfi['date'], format="%Y-%m-%d %H:%M:%S%z")
    nftfi['loan_start_time'] = pd.to_datetime(nftfi['loan_start_time'], format="%Y-%m-%d %H:%M:%S%z")
    nftfi['loan_repaid_time'] = pd.to_datetime(nftfi['loan_repaid_time'], format="%Y-%m-%d %H:%M:%S%z")
    nftfi['loan_type'] = nftfi.loan_no.astype(str).str.split('-').apply(lambda x: x[0] + '-' + x[1] if len(x) > 2 else x[0])

    # Remove invalid values
    nftfi.replace(r"#DIV/0!", np.nan, regex=True, inplace=True)
    nftfi.replace(r"#N/A", "", regex=True, inplace=True)

    # Divide the currency by its respective divider
    # now map missing usd_value, e.g. for stablecoin-denominated loans
    usdc_address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'  # https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48
    usdt_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'  # https://etherscan.io/token/0xdac17f958d2ee523a2206206994597c13d831ec7
    dai_address = '0x6B175474E89094C44Da98b954EedeAC495271d0F'  # https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f
    weth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

    columns_to_clean = ['loan_principal_amount', 'maximum_repayment_amount', 'maximum_repayment_amount']  # Divide loanPrincipalAmount and maximumRepaymentAmount by ETH <> WEI i.e. 1^18
    for col in columns_to_clean:
        nftfi[col] = nftfi[col].astype(np.float64)
        nftfi.loc[nftfi['loan_erc20denomination'] == weth_address, col] /= 10 ** 18
        nftfi.loc[nftfi['loan_erc20denomination'] == dai_address, col] /= 10 ** 18
        nftfi.loc[nftfi['loan_erc20denomination'] == usdc_address, col] /= 10 ** 6

    # nftfi['no_of_days'] = nftfi['no_of_days'].astype(np.float64)
    nftfi = nftfi.rename(columns={'loan_apr': 'apr'})
    nftfi['apr'] = nftfi['apr'].astype(np.float64)

    # Drop last column as it is unnamed
    nftfi = nftfi.drop('', axis=1, errors='ignore')

    # set BOOL columns to bool type
    cols = ['repaid', 'liquidated']
    nftfi['repaid'] = nftfi['repaid'].fillna(False)
    nftfi['repaid'] = nftfi['repaid'].replace('', False)
    for col in cols:
        # nftfi[col] = nftfi[col].astype('boolean')
        nftfi[col] = nftfi[col].map({'True': True, 'False': False})
        nftfi[col] = nftfi[col].astype(bool)
    nftfi['repaid'] = nftfi['repaid'].astype(bool)
    # Enrich dataset with ETHUSD rate i.e. ETHPrice, then fill USDValue for USDValue from loanERC20Denomination == weth_address
    weth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'.lower()
    price_df = pd.read_csv('analysis/metaquants_analysis/loans_eth_usd_input_data.csv')
    price_df = price_df.rename(columns={'datetime': 'date'})
    price_df['date'] = pd.to_datetime(price_df['date'], format='%Y-%m-%d %H:%M:%S%z')
    price_df = price_df.drop(columns=['open', 'low', 'volume'])

    nftfi['date'] = pd.to_datetime(nftfi['date'])
    nftfi['loan_principal_amount'] = nftfi['loan_principal_amount'].astype(float)

    nftfi = nftfi.sort_values(by='date')
    price_df = price_df.sort_values(by='date')

    nftfi = pd.merge_asof(nftfi, price_df, on='date', direction='backward')
    nftfi['eth_price'] = nftfi['close']
    nftfi = nftfi.drop(columns=['close'])
    nftfi['loan_erc20denomination'] = nftfi['loan_erc20denomination'].astype(str).str.lower().str.strip()
    nftfi.loc[nftfi['loan_erc20denomination'] == weth_address, 'usd_value'] = nftfi.loc[nftfi['loan_erc20denomination'] == weth_address]['loan_principal_amount'] * nftfi.loc[nftfi['loan_erc20denomination'] == weth_address]['eth_price']

    # now map missing usd_value, e.g. for stablecoin-denominated loans
    usdc_address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'  # https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48
    usdt_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'  # https://etherscan.io/token/0xdac17f958d2ee523a2206206994597c13d831ec7
    dai_address = '0x6B175474E89094C44Da98b954EedeAC495271d0F'  # https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f
    stablecoin_addresses = [usdc_address, usdt_address, dai_address]
    for stablecoin_address in stablecoin_addresses:
        stablecoin_address = stablecoin_address.lower()
        nftfi.loc[nftfi['loan_erc20denomination'] == stablecoin_address, 'usd_value'] = nftfi.loc[nftfi['loan_erc20denomination'] == stablecoin_address]['loan_principal_amount']

    nftfi_loan_no_count = pd.DataFrame(nftfi.groupby('loan_no').agg('count')['borrower'])
    duplicated_nftfi_loans = pd.merge(left=nftfi, right=nftfi_loan_no_count.loc[nftfi_loan_no_count['borrower']>1], left_on='loan_no', right_on='loan_no')

    # Check if it can be due to missing token
    usdc_address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'  # https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48
    usdt_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'  # https://etherscan.io/token/0xdac17f958d2ee523a2206206994597c13d831ec7
    dai_address = '0x6B175474E89094C44Da98b954EedeAC495271d0F'  # https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f
    weth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

    stablecoin_addresses = [usdc_address, usdt_address, dai_address, weth_address]

    stablecoin_names = ['usdc', 'usdt', 'dai', 'weth']
    for stablecoin_address, stablecoin_name in zip(stablecoin_addresses, stablecoin_names):
        stablecoin_address = stablecoin_address.lower()
        nftfi.loc[nftfi['loan_erc20denomination'] == stablecoin_address, 'loan_erc20denomination_name'] = stablecoin_name
    return nftfi


# Function to load the data
def load_data(filename):
    return pd.read_csv(filename)


def run_tests():
    filenames = [f"data/mq_df1_data_{num}.csv" for num in range(1, 6)]
    dataframes = [load_data(filename) for filename in filenames]

    # Use the first DataFrame as the baseline for comparison
    baseline_dataframe = dataframes[0]

    # Compare each DataFrame to the baseline
    for df in dataframes[1:]:
        assert_frame_equal(baseline_dataframe, df)


def match_min_max_dates(df1, df2):
    # Check minimum and maximum dates of each table
    print(f"min df1 date: {df1.block_timestamp.min()}; max df1 date: {df1.block_timestamp.max()}")
    print(f"min df2 date: {df2.block_timestamp.min()}; max df2 date: {df2.block_timestamp.max()}")

    if df2['block_timestamp'].min() > df1['block_timestamp'].min():
        # df1 has more complete dataset
        df1 = df1.loc[df1['block_timestamp'] >= df2['block_timestamp'].min()]
    else:
        # df2 has more complete dataset
        df2 = df2.loc[df2['block_timestamp'] >= df1['block_timestamp'].min()]

    if df2['block_timestamp'].max() > df1['block_timestamp'].max():
        # df2 has more complete dataset
        df2 = df2.loc[df2['block_timestamp'] <= df1['block_timestamp'].max()]
    else:
        # df1 has more complete dataset
        df1 = df1.loc[df1['block_timestamp'] <= df2['block_timestamp'].max()]

    print('\n\n --------------- AFTER')
    # Check minimum and maximum dates of each table
    print(f"min df1 date: {df1.block_timestamp.min()}; max df1 date: {df1.block_timestamp.max()}")
    print(f"min df2 date: {df2.block_timestamp.min()}; max df2 date: {df2.block_timestamp.max()}\n\n")
    return df1, df2


def match_on_dates(df1, df2, start='2020-04-01', end='2024-05-01'):
    df1_subfiltered = df1.loc[df1['block_timestamp'] >= start].loc[df1['block_timestamp'] < end]
    print(df1_subfiltered.shape)
    df2_subfiltered = df2.loc[df2['block_timestamp'] >= start].loc[df2['block_timestamp'] < end]
    print(df2_subfiltered.shape)
    return df1_subfiltered, df2_subfiltered

def compare_unique_rows(df1, df2):

    # how do i get all rows in df1 that are not in df2
    # and all rows in df2 that are not in df1?

    # Perform a full outer join on df1 and df2
    full_outer = pd.merge(df1, df2, how='outer', on='transaction_hash', indicator=True)

    # Filter out the rows that are unique to df1
    unique_to_df1 = full_outer[full_outer['_merge'] == 'left_only']

    # Filter out the rows that are unique to df2
    unique_to_df2 = full_outer[full_outer['_merge'] == 'right_only']

    print(f"number of loans unique to df1 relative to df2: {unique_to_df1.shape[0]}, i.e. {100 * round(unique_to_df1.shape[0] / df1.shape[0], 2)}%")
    print(f"while df1 had {df1.shape[0]} loans while df2 had {df2.shape[0]}, i.e. df1 has {df1.shape[0] - df2.shape[0]} more loans")
    print(unique_to_df1.shape[0])
    print(unique_to_df1)

    print(f"number of loans unique to df2 relative to df1: {unique_to_df2.shape[0]}, i.e. {100 * round(unique_to_df2.shape[0] / df2.shape[0], 2)}%")
    print(f"while df1 had {df1.shape[0]} loans while df2 had {df2.shape[0]}, i.e. df1 has {df1.shape[0] - df2.shape[0]} more loans")

    print(unique_to_df2.shape[0])
    print(unique_to_df2)

    nftfi = load_nftfi_table()
    unique_to_df2['loan_id_y'] = unique_to_df2['loan_id_y'].astype(int)
    nftfi['loan_no_cleaned'] = nftfi['loan_no_cleaned'].astype(int)
    unique_to_df2_enriched_with_nftfi = pd.merge(unique_to_df2, nftfi, left_on='loan_id_y', right_on='loan_no_cleaned', how='inner')
    assert unique_to_df2_enriched_with_nftfi.shape[0] == unique_to_df2.shape[0], "Loans unique to API data (presumably V1 loans) does not match 1 for 1 with NFTfi!"
    print(unique_to_df2_enriched_with_nftfi)


def run_test_with_baseline():
    baseline_dataframe = load_data("data/metaquants_loans.csv")

    filename = f"data/mq_nftfi_data_1.csv"
    api_dataframe = load_data(filename)

    print(f"min baseline_dataframe date: {baseline_dataframe.block_timestamp.min()}; max baseline_dataframe date: {baseline_dataframe.block_timestamp.max()}")
    print(f"min api_dataframe date: {api_dataframe.block_timestamp.min()}; max api_dataframe date: {api_dataframe.block_timestamp.max()}")

    # baseline_dataframe, api_dataframe = match_min_max_dates(df1=baseline_dataframe, df2=api_dataframe)
    baseline_dataframe, api_dataframe = match_on_dates(df1=baseline_dataframe, df2=api_dataframe, start='2023-01-01', end='2023-05-01')

    compare_unique_rows(df1=baseline_dataframe, df2=api_dataframe)

    assert_frame_equal(baseline_dataframe, api_dataframe)



