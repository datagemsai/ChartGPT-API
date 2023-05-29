# from analytics_bot_langchain.data.merge_MQ_rchen_data import merge_nftfi_volume_per_collection, merge_daily_nftfi_loan_volume

# from analytics_bot_langchain.data.merge_borrow_volume_df import run
from analysis.apr_clusters import apr_ranges_nftfi
from analysis.nabu_api import analysis

analysis.run_for_all()

# merge_nftfi_volume_per_collection()
# merge_daily_nftfi_loan_volume()

