from dataclasses import dataclass
from typing import List


@dataclass
class Dataset:
    name: str
    id: str
    description: str
    sample_questions: List[str]

    def __repr__(self):
        return self.name


datasets = [
    Dataset(
        name="Decentralized Exchange Trades",
        id="dex_trades",
        description="A dataset of decentralized exchange (DEX) transactions across L1 and L2 blockchains.",
        sample_questions=[
            "Perform EDA",
            "Plot a pie chart of the top 5 takers with highest transaction count, group the remainder takers as Others category",
            "Plot top 5 projects by transaction count",
            "Plot the pairs corresponding to the largest USDC transactions",
            "Plot the highest USD transactions grouped by blockchain",
            "Plot the highest trade count grouped by blockchain and trading pair",
        ]
    ),
    Dataset(
        name="NFT Lending Protocol Aggregate Borrow Volume",
        id="nft_lending_aggregated_borrow",
        description="A dataset of the aggregate borrow volume for different NFT lending protocols.",
        sample_questions=[
            "Perform EDA",
            "Plot the monthly loan volume grouped by protocol",
            "Plot a stacked bar chart of loan volume grouped by protocol since August 2022",
            "Plot top 3 protocols on April 3rd 2023",
            "Plot daily borrow volumes for each protocol in February 2023",
            "Plot monthly cumulative borrow volumes for each protocol",
        ],
    ),
    Dataset(
        name="Growjo - Fastest Growing Companies",
        id="growjo_fastest_growing_companies",
        description="Analyse the fastest growing companies in the AI & Analytics space according to Growjo.",
        sample_questions=[
            "Perform EDA",
            "Plot total funding by country",
            "Plot the average valuation for US Analytics companies by State",
            "Plot top 5 companies by job openings",
            "What is the average number of employees for AI companies from CA state",
            "Plot the average revenue for companies from following four states: CA, TX, MA, NY",
        ],
    ),
    Dataset(
        name="NFT Lending Aggregated by NFT Collection",
        id="nft_lending_aggregated_nft_collection",
        description="Borrowed dollar amounts and number of NFTs locked for each NFT collection",
        sample_questions=[
            "Perform EDA",
            "Give me three visualizations",
            "Tell me more about Azuki and Artblocks",
            "Plot borrow_usd on one y-axis, num_unique_nft on a secondary y-axis, grouped by Bored Ape Yacht Club, Azuki and Wrapped Cryptopunks, and the remainder collections displayed as Others",
        ],
    ),
    Dataset(
        name="NFT Lending data by Metaquants",
        id="nft_finance_p2p_p2pool",
        description="",
        sample_questions=[
            "Perform EDA",
            "Give me three visualizations",
            "Tell me more about Azuki and Artblocks",
            "Plot borrow_usd on one y-axis, num_unique_nft on a secondary y-axis, grouped by Bored Ape Yacht Club, Azuki and Wrapped Cryptopunks, and the remainder collections displayed as Others",
        ],
    )

]
