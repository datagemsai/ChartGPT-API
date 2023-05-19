import pandas as pd

from analytics_bot_langchain.data import metaquants

import pandas
# df = pd.read_csv('analytics_bot_langchain/data/metaquants/nft_finance_p2p.csv')
# df2 = pd.read_csv('analytics_bot_langchain/data/metaquants/nft_finance_p2pool.csv')
# exit(0)
from analytics_bot_langchain.data.bigquery_pipeline import run, clean_local_csv_files, Datatype

# run()
clean_local_csv_files(Datatype.nftfi_loan_data, table_name='nftfi_loan_data', dune_query=False)
# metaquants.run_for_all()

