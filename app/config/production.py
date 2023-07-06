from app.config import Dataset, Table


datasets = [
    Dataset(
        name="MetaQuants NFT Finance Aggregator",
        id="metaquants_nft_finance_aggregator",
        description="""
        Leverage the MetaQuants NFT Finance Aggregator to gain valuable insights into NFT loan history, outstanding loan indicators, and activity on both P2Peer and P2Pool protocols. The dataset currently includes a range of leading providers, including X2Y2, Pine, BendDAO, ***REMOVED***, Arcade, and JPEGD.        
        """,
        sample_questions=[
            "Perform EDA",
            "What is the top P2P protocol by lending volume?",
            "Plot the monthly loan volume grouped by protocol",
            "Plot a stacked bar chart of loan volume grouped by protocol since August 2022",
            "Plot top 3 protocols on April 3rd 2023",
            "Plot daily borrow volumes for each protocol in February 2023",
            "Plot monthly cumulative borrow volumes for each protocol",
        ]
    ),
    # Table(
    #     name="MetaQuants",
    #     project_id="chartgpt-production",
    #     dataset_id="metaquants_nft_finance_aggregator",
    #     table_id="metaquants_nft_finance_aggregator_p2p",
    #     description="A dataset of decentralized exchange (DEX) transactions across L1 and L2 blockchains.",
    #     sample_questions=[
    #         "Perform EDA",
    #         "Plot a pie chart of the top 5 takers with highest transaction count, group the remainder takers as Others category",
    #         "Plot top 5 projects by transaction count",
    #         "Plot the pairs corresponding to the largest USDC transactions",
    #         "Plot the highest USD transactions grouped by blockchain",
    #         "Plot the highest trade count grouped by blockchain and trading pair",
    #     ]
    # ),
]
