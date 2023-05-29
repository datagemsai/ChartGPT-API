import pandas as pd


def merge_daily_nftfi_loan_volume():
    data_dir = 'analytics_bot_langchain/data/metaquants/'
    metaquants = pd.read_csv(f'{data_dir}MQ_nftfi_data.csv')
    rchen = pd.read_csv(f'{data_dir}rchen8_daily_nftfi_loan_volume.csv')
    nftfi = pd.read_csv(f'{data_dir}NFTFI_daily_borrow_volume.csv')

    metaquants['date'] = pd.to_datetime(metaquants['date']).dt.date
    rchen['date'] = pd.to_datetime(rchen['date_trunc(day, evt_block_time)']).dt.date
    nftfi['date'] = pd.to_datetime(nftfi['date']).dt.date
    nftfi = nftfi.rename(columns={'borrow_volume': 'NFTFI borrow_volume'})
    rchen = rchen.drop(columns=['date_trunc(day, evt_block_time)'])
    rchen = rchen.rename(columns={'usd': 'rchen8 borrow_volume'})

    df = pd.merge(left=metaquants, right=rchen, left_on='date', right_on='date', how='left')
    df = pd.merge(left=nftfi, right=df, left_on='date', right_on='date', how='left')
    df.to_csv('borrow_volume.csv', index=False)
    print(df)
    return df


def merge_nftfi_volume_per_collection():
    data_range_str = 'april_2023'

    data_dir = 'analytics_bot_langchain/data/metaquants/'

    # collection_address,protocol,past_month_amt_usd,all_time_amt_usd
    metaquants = pd.read_csv(f'{data_dir}MQ_one_month_and_all_time_nftfi_borrow_volume_per_collection_april_2023.csv')
    # name,nftCollateralContract,all_time,past_month
    rchen = pd.read_csv(f'{data_dir}rchen8_collection_loan_volume_april2023.csv')
    # collection_name,nft_collateral_contract,april_2023_usd_value,all_time_usd_value
    nftfi = pd.read_csv(f'{data_dir}NFTFI_one_month_and_all_time_nftfi_borrow_volume_per_collection_april_2023.csv')
    nftfi = nftfi.rename(columns={'nft_collateral_contract': 'collection_address',
                                  'april_2023_usd_value': f'NFTFI_{data_range_str}_borrow_volume',
                                  'all_time_usd_value': f'NFTFI_all_time_borrow_volume',
                                  }
                         )

    metaquants = metaquants.drop(columns=['protocol'])
    metaquants = metaquants.rename(columns={'all_time_amt_usd': 'MQ_all_time_borrow_volume', 'past_month_amt_usd': f'MQ_{data_range_str}_borrow_volume'})

    rchen['past_month'] = rchen['past_month'].fillna(0)
    rchen['past_month'] = rchen['past_month'].replace('', 0.0).astype(float)
    rchen = rchen.rename(columns={'all_time': 'rchen8_all_time_borrow_volume', 'past_month': f'rchen8_{data_range_str}_borrow_volume', 'nftCollateralContract': 'collection_address'})

    df = pd.merge(left=metaquants, right=rchen, on='collection_address', how='left')
    df = pd.merge(left=nftfi, right=df, on='collection_address', how='left')
    print(df.columns)
    df = df[['name', 'collection_address', 'MQ_all_time_borrow_volume', f'NFTFI_all_time_borrow_volume', 'rchen8_all_time_borrow_volume', f'MQ_{data_range_str}_borrow_volume', f'NFTFI_{data_range_str}_borrow_volume', f'rchen8_{data_range_str}_borrow_volume']]
    df = df.sort_values('MQ_all_time_borrow_volume', ascending=False)
    print(df)

    df.to_csv(f'{data_dir}MQ_NFTFI_rchen8_one_month_and_all_time_nftfi_borrow_volume_per_collection_{data_range_str}.csv', index=False)

    return df


