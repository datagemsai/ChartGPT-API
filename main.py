import pandas as pd

from analytics_bot_langchain.data import metaquants

import pandas
df = pd.read_csv('analytics_bot_langchain/data/metaquants/nft_finance_p2p.csv')
df2 = pd.read_csv('analytics_bot_langchain/data/metaquants/nft_finance_p2pool.csv')
exit(0)


metaquants.run_for_all()

