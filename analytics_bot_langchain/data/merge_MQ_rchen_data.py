import pandas as pd


def merge_daily_nftfi_loan_volume():
    metaquants = pd.read_csv('analytics_bot_langchain/data/metaquants/MQ_nftfi_data.csv')
    rchen = pd.read_csv('rchen8_daily_nftfi_loan_volume.csv')

    metaquants['date'] = pd.to_datetime(metaquants['date']).dt.date
    rchen['date'] = pd.to_datetime(rchen['date_trunc(day, evt_block_time)']).dt.date
    rchen = rchen.drop(columns=['date_trunc(day, evt_block_time)'])
    rchen = rchen.rename(columns={'usd': 'rchen8 borrow_volume'})

    df = pd.merge(left=metaquants, right=rchen, left_on='date', right_on='date', how='left')
    df.to_csv('borrow_volume.csv', index=False)
    print(df)
    return df


def merge_nftfi_volume_per_collection():
    data_dir = 'analytics_bot_langchain/data/metaquants/'

    # collection_address,protocol,past_month_amt_usd,all_time_amt_usd
    metaquants = pd.read_csv(f'{data_dir}MQ_one_month_and_all_time_nftfi_borrow_volume_per_collection.csv')
    # name,nftCollateralContract,all_time,past_month
    rchen = pd.read_csv(f'{data_dir}rchen8_collection_loan_volume.csv')

    metaquants = metaquants.drop(columns=['protocol'])
    rchen = rchen.rename(columns={'all_time': 'rchen8_all_time_borrow_volume', 'past_month': 'rchen8_past_month_borrow_volume', 'nftCollateralContract': 'collection_address'})
    metaquants = metaquants.rename(columns={'all_time_amt_usd': 'MQ_all_time_borrow_volume', 'past_month_amt_usd': 'MQ_past_month_borrow_volume'})

    df = pd.merge(left=metaquants, right=rchen, on='collection_address', how='left')
    print(df.columns)
    df = df[['name', 'collection_address', 'MQ_all_time_borrow_volume', 'rchen8_all_time_borrow_volume', 'MQ_past_month_borrow_volume', 'rchen8_past_month_borrow_volume']]
    print(df)
    df.to_csv(f'{data_dir}MQ_rchen8_one_month_and_all_time_nftfi_borrow_volume_per_collection.csv', index=False)
    return df


