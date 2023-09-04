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
            "Give me a description of each of the columns in the dataset.",
            "Which protocol provided the lowest APRs in the past month?",
            "Plot the average APR for the ***REMOVED*** protocol in the past 6 months.",
            "Plot a bar chart of the USD lending volume for all protocols.",
            "Plot a stacked area chart of the USD lending volume for all protocols.",
        ],
    ),
]
