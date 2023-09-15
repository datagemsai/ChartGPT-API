from app.config.datasets import (Dataset, get_dataset_description,
                                 get_table_description)

datasets = [
    Dataset(
        name="MetaQuants NFT Finance Aggregator",
        project="chartgpt-staging",
        id="metaquants_nft_finance_aggregator",
        description="""
        Leverage the MetaQuants NFT Finance Aggregator to gain valuable insights into NFT loan history, outstanding loan indicators, and activity on both P2Peer and P2Pool protocols. The dataset currently includes a range of leading providers, including X2Y2, Pine, BendDAO, NFTfi, Arcade, and JPEGD.        
        
        Data source: https://metaquants.xyz/

        Updated daily at 12AM CET.
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
        name="USA Real Estate Listings",
        project="chartgpt-staging",
        id="real_estate",
        description="""
        Real Estate listings (900k+) in the US categorised by State and zip code.

        Data source: https://www.kaggle.com/datasets/ahmedshahriarsakib/usa-real-estate-dataset
        """,
        tables=[
            "usa_real_estate_listings",
        ],
    ),
    Dataset(
        name="Ethereum Blockchain Transactions",
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
    Dataset(
        name="Ethereum Classic Blockchain Transactions",
        project="bigquery-public-data",
        id="crypto_ethereum_classic",
        description=get_table_description(
            "bigquery-public-data", "crypto_ethereum_classic", "transactions"
        ),
        tables=[
            # "token_transfers",
            "transactions"
        ],
        sample_questions=[
            "Plot the number of transactions over time for transactions with a value over 0 Wei."
        ],
    ),
    Dataset(
        name="Bitcoin Blockchain Transactions",
        project="bigquery-public-data",
        id="crypto_bitcoin",
        description=get_table_description(
            "bigquery-public-data", "crypto_bitcoin", "transactions"
        ),
        tables=[
            # "token_transfers",
            "transactions"
        ],
        sample_questions=[
            "Plot the number of transactions over time for transactions with a value over 0 Wei."
        ],
    ),
    Dataset(
        name="Polygon Blockchain Transactions",
        project="public-data-finance",
        id="crypto_polygon",
        description=get_table_description(
            "public-data-finance", "crypto_polygon", "transactions"
        ),
        tables=[
            "transactions"
        ],
        sample_questions=[
            "Plot the number of transactions over time for transactions with a value over 0 Wei."
        ],
    ),
    Dataset(
        name="Dash Blockchain Transactions",
        project="bigquery-public-data",
        id="crypto_dash",
        description=get_table_description(
            "bigquery-public-data", "crypto_dash", "transactions"
        ),
        tables=[
            "transactions"
        ],
    ),
    Dataset(
        name="Dogecoin Blockchain Transactions",
        project="bigquery-public-data",
        id="crypto_dogecoin",
        description=get_table_description(
            "bigquery-public-data", "crypto_dogecoin", "transactions"
        ),
        tables=[
            "transactions"
        ],
    ),
    # Dataset(
    #     name="US Residential Real Estate Sample Data",
    #     project="housecanary-com",
    #     id="sample",
    #     description="Time series of median home value per block designated as single family residential (SFD), condominium (CND), or townhouse (TH).",
    #     tables=[
    #         "block_value_ts",
    #     ],
    #     sample_questions=[
    #         "Plot the average property value over time for single family residential properties.",
    #         "Plot the average property value over time for all property types.",
    #     ],
    # ),
    # Dataset(
    #     name="Google Analytics Sample Data",
    #     project="bigquery-public-data",
    #     id="google_analytics_sample",
    #     description=get_table_description(
    #         "bigquery-public-data", "google_analytics_sample", "ga_sessions_20170801"
    #     ),
    #     tables=["ga_sessions_20170801"],
    #     sample_questions=[
    #         "Which Google Analytics channel provides the highest number of visitors?",
    #         "Which device accounts for the highest number of visitors?",
    #     ],
    # ),
]
