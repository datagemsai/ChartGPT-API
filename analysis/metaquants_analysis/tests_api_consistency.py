# %%
import pandas as pd
import unittest
from pandas.testing import assert_frame_equal

# Function to load the data
def load_data(filename):
    return pd.read_csv(filename)


def run_tests():
    filenames = [f"data/mq_nftfi_data_{num}.csv" for num in range(1, 6)]
    dataframes = [load_data(filename) for filename in filenames]

    # Use the first DataFrame as the baseline for comparison
    baseline_dataframe = dataframes[0]

    # Compare each DataFrame to the baseline
    for df in dataframes[1:]:
        assert_frame_equal(baseline_dataframe, df)

# %%



