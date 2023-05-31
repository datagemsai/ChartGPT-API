import pandas as pd

from analysis.metaquants_analysis.tests_api_consistency import run_tests, run_test_with_baseline
from analytics_bot_langchain.data.merge_MQ_rchen_data import merge_nftfi_volume_per_collection, merge_daily_nftfi_loan_volume

# from analytics_bot_langchain.data.merge_borrow_volume_df import run


# merge_nftfi_volume_per_collection()
# merge_daily_nftfi_loan_volume()
# run_tests()
run_test_with_baseline()

