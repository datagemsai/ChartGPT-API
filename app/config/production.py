from app.config import Dataset


datasets = [
    Dataset(
        name="MetaQuants NFT Finance Aggregator",
        id="metaquants_nft_finance_aggregator",
        description="""
        Leverage the MetaQuants NFT Finance Aggregator to gain valuable insights into NFT loan history, outstanding loan indicators, and activity on both P2Peer and P2Pool protocols. The dataset currently includes a range of leading providers, including X2Y2, Pine, BendDAO, NFTfi, Arcade, and JPEGD.        
        """,
        tables=[
            "metaquants_nft_finance_aggregator_all",
        ],
        sample_questions=[
            "Perform EDA",
            "Give me a description of each of the columns in the dataset",
            "Plot the average APR for the NFTfi platform in the last 3 months",
            "What is the top P2P protocol by lending volume?",
            "Plot the monthly loan volume grouped by protocol",
            "Plot a stacked bar chart of loan volume grouped by protocol since August 2022",
            "Plot top 3 protocols on April 3rd 2023",
            "Plot daily borrow volumes for each protocol in February 2023",
            "Plot monthly cumulative borrow volumes for each protocol",
        ]
    ),
]
