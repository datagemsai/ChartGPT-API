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
    metaquants = pd.read_csv('analytics_bot_langchain/data/metaquants/MQ_one_month_and_all_time_nftfi_borrow_volume_per_collection.csv')
    rchen = pd.read_csv('rchen8_collection_loan_volume.csv')

    metaquants['date'] = pd.to_datetime(metaquants['date']).dt.date
    rchen['date'] = pd.to_datetime(rchen['date_trunc(day, evt_block_time)']).dt.date
    rchen = rchen.drop(columns=['date_trunc(day, evt_block_time)'])
    rchen = rchen.rename(columns={'usd': 'rchen8 borrow_volume'})

    df = pd.merge(left=metaquants, right=rchen, left_on='date', right_on='date', how='left')
    df.to_csv('borrow_volume.csv', index=False)
    print(df)
    return df


