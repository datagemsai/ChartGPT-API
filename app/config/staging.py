from app.config import Dataset


datasets = [
    Dataset(
        name="MetaQuants NFT Finance Aggregator",
        id="metaquants_nft_finance_aggregator",
        description="""
        Leverage the MetaQuants NFT Finance Aggregator to gain valuable insights into NFT loan history, outstanding loan indicators, and activity on both P2Peer and P2Pool protocols. The dataset currently includes a range of leading providers, including X2Y2, Pine, BendDAO, ***REMOVED***, Arcade, and JPEGD.        
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
            "Give me a description of each of the columns in the dataset",
            "Plot the average APR for the ***REMOVED*** platform in the last 3 months",
            "What is the top P2P protocol by lending volume?",
            "Plot the monthly loan volume grouped by protocol",
            "Plot a stacked bar chart of loan volume grouped by protocol since August 2022",
            "Plot top 3 protocols on April 3rd 2023",
            "Plot daily borrow volumes for each protocol in February 2023",
            "Plot monthly cumulative borrow volumes for each protocol",
        ]
    ),
]
