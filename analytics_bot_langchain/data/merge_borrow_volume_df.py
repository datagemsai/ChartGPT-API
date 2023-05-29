import pandas as pd


def run_daily_borrow_volume():
    metaquants = pd.read_csv('metaquants_nftfi_data.csv')
    rchen = pd.read_csv('daily_nftfi_loan_volume.csv')

    metaquants['date'] = pd.to_datetime(metaquants['date']).dt.date
    rchen['date'] = pd.to_datetime(rchen['date_trunc(day, evt_block_time)']).dt.date
    rchen = rchen.drop(columns=['date_trunc(day, evt_block_time)'])
    rchen = rchen.rename(columns={'usd': 'rchen8 borrow_volume'})

    df = pd.merge(left=metaquants, right=rchen, left_on='date', right_on='date', how='left')
    df.to_csv('borrow_volume.csv')
    print(df)
    return df


def run_last_month_borrow_volume_per_collection():
    metaquants = pd.read_csv('metaquants_nftfi_data.csv')
    rchen = pd.read_csv('daily_nftfi_loan_volume.csv')

    metaquants['date'] = pd.to_datetime(metaquants['date']).dt.date
    rchen['date'] = pd.to_datetime(rchen['date_trunc(day, evt_block_time)']).dt.date
    rchen = rchen.drop(columns=['date_trunc(day, evt_block_time)'])
    rchen = rchen.rename(columns={'usd': 'rchen8 borrow_volume'})

    df = pd.merge(left=metaquants, right=rchen, left_on='date', right_on='date', how='left')
    df.to_csv('borrow_volume.csv')
    print(df)
    return df