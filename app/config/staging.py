from app.config.datasets import (Dataset, get_dataset_description,
                                 get_table_description)

datasets = [
    Dataset(
        name="MetaQuants NFT Finance Aggregator",
        project="chartgpt-staging",
        id="metaquants_nft_finance_aggregator",
        description="""
        Leverage the MetaQuants NFT Finance Aggregator to gain valuable insights into NFT loan history, outstanding loan indicators, and activity on both P2Peer and P2Pool protocols. The dataset currently includes a range of leading providers, including X2Y2, Pine, BendDAO, NFTfi, Arcade, and JPEGD.        
        """,
        tables=[
            "p2p_and_p2pool_loan_data_borrow",
        ],
        column_descriptions={
            "from_address": "Only relevant for protocols nftfi, x2y2, blend, arcade",
            "principal_amount": "Only relevant for protocols nftfi, x2y2, blend, arcade",
            "repayment_amount": "Only relevant for protocols nftfi, x2y2, arcade",
            "due_date": "Only relevant for protocols nftfi, x2y2, arcade",
            "duration_in_days": "Only relevant for protocols nftfi, x2y2, arcade",
            "apr": "Only relevant for protocols nftfi, x2y2, blend, arcade",
            "amt_in_usd": "Only relevant for protocols bend, jpegd, nftfi, x2y2, blend, arcade",
            "roll_over": "Only relevant for protocols blend, arcade",
        },
        sample_questions=[
            "Perform EDA",
            "Give me a description of each of the columns in the dataset.",
            "Which protocol provided the lowest APRs in the past month?",
            "Plot the average APR for the NFTfi protocol in the past 6 months.",
            "Plot a bar chart of the USD lending volume for all protocols.",
            "Plot a stacked area chart of the USD lending volume for all protocols.",
        ],
    ),
    Dataset(
        name="US Residential Real Estate Sample Data",
        project="housecanary-com",
        id="sample",
        description="Time series of median home value per block designated as single family residential (SFD), condominium (CND), or townhouse (TH).",
        tables=[
            "block_value_ts",
        ],
        sample_questions=[
            "Plot the average value over time for single family residential properties."
        ],
    ),
    Dataset(
        name="Google Analytics Sample Data",
        project="bigquery-public-data",
        id="google_analytics_sample",
        description=get_table_description(
            "bigquery-public-data", "google_analytics_sample", "ga_sessions_20170801"
        ),
        tables=["ga_sessions_20170801"],
        sample_questions=[
            "Which Google Analytics channel provides the highest number of visitors?",
            "Which device accounts for the highest number of visitors?",
        ],
    ),
    Dataset(
        name="Ethereum Blockchain Transactions Sample Data",
        project="bigquery-public-data",
        id="crypto_ethereum",
        description=get_table_description(
            "bigquery-public-data", "crypto_ethereum", "transactions"
        ),
        tables=[
            # "token_transfers",
            "transactions"
        ],
        sample_questions=[
            "Plot the number of transactions over time for transactions with a value over 0 Wei."
        ],
    ),
]
