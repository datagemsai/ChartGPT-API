from app.config.datasets import (Dataset, get_dataset_description,
                                 get_table_description)

datasets = [
    Dataset(
        name="MetaQuants NFT Finance Aggregator",
        project="chartgpt-staging",
        id="metaquants_nft_finance_aggregator",
        description="""
        Leverage the MetaQuants NFT Finance Aggregator to gain valuable insights into NFT loan history, outstanding loan indicators, and activity on both P2Peer and P2Pool protocols. The dataset currently includes a range of leading providers, including X2Y2, Pine, BendDAO, NFTfi, Arcade, and JPEGD.        
        
        Data source: https://metaquants.xyz/, updated daily at 12AM CET.
        """,
        tables=[
            "p2p_and_p2pool_loan_data_borrow",
        ],
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
        sample_questions=[
            "Which state has had the most stable increase in property prices over the past 10 years?",
        ]
    ),
    Dataset(
        name="Ethereum Blockchain Transactions",
        project="bigquery-public-data",
        id="crypto_ethereum",
        description="""
        Each block in the blockchain is composed of zero or more transactions.
        Each transaction has a source address, a target address, an amount of Ether transferred, and an array of input bytes.
        This table contains a set of all transactions from all blocks, and contains a block identifier to get associated block-specific information associated with each transaction.
        Data is exported using https://github.com/medvedev1088/ethereum-etl

        Data source: https://console.cloud.google.com/marketplace/product/ethereum/crypto-ethereum-blockchain
        """,
        tables=[
            "transactions"
        ],
        sample_questions=[
            "Plot the number of transactions over time for the past year.",
            # "Plot a NetworkX graph of the largest 100 transactions in the past year."
        ],
    ),
    Dataset(
        name="Bitcoin Blockchain Transactions",
        project="bigquery-public-data",
        id="crypto_bitcoin",
        description="""
        Bitcoin is a crypto currency leveraging [blockchain technology](https://en.wikipedia.org/wiki/Blockchain)
        to store transactions in a distributed ledger.
        A blockchain is an ever-growing [tree](https://en.wikipedia.org/wiki/Tree_(data_structure))  of blocks. Each block contains a number of transactions.
        To learn more, read the [Bitcoin Wiki](https://en.bitcoin.it/wiki/Block).

        This dataset is part of a larger effort to make cryptocurrency data available in BigQuery
        through the [Google Cloud Public Datasets program](https://cloud.google.com/public-datasets). 
        The program is hosting several cryptocurrency datasets, with plans to both expand offerings
        to include additional cryptocurrencies and reduce the latency of updates.

        Data source: https://console.cloud.google.com/marketplace/product/bitcoin/crypto-bitcoin
        """,
        tables=[
            "transactions"
        ],
        sample_questions=[
            "Plot the number of transactions over time for the past year.",
            # "Plot a NetworkX graph of the largest 100 transactions in the past year."
        ],
    ),
    Dataset(
        name="Polygon Blockchain Transactions",
        project="public-data-finance",
        id="crypto_polygon",
        description="""
        [Polygon Technology](https://polygon.technology/) is Ethereum's Internet of Blockchain. We bring massive scale to Ethereum via Polygon SDK
        supporting stand alone chains and secured chains.
        This dataset is part of a larger effort to make cryptocurrency data available in BigQuery through
        the Google Cloud Public Datasets Program. The program is hosting several cryptocurrency datasets,
        with plans to both expand offerings to include additional cryptocurrencies and reduce the latency of updates.

        Data source: https://console.cloud.google.com/marketplace/product/public-data-finance/crypto-polygon-dataset
        """,
        tables=[
            "transactions"
        ],
        sample_questions=[
            "Plot the number of transactions over time for the past year.",
            # "Plot a NetworkX graph of the largest 100 transactions in the past year."
        ],
    ),
]
