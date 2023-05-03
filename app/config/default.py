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
        name = "Ethereum Decentralized Exchange Transactions",
        # TODO Rename as follows
        # id = "ethereum_dex_transactions",
        id = "ethereum_dex_transactions",
        description = "A dataset of decentralized exchange (DEX) transactions on the Ethereum Blockchain.",
        sample_questions = [
            "Plot a pie chart of the top 5 takers with highest transaction count, group the remainder takers as Others category",
            "Plot top 5 projects by transaction count",
            "Plot the pairs corresponding to the largest USDC transactions",
            "Plot the highest USD transactions grouped by blockchain",
            "Plot the highest trade count grouped by blockchain and trading pair"
        ]
    ),
    Dataset(
        name = "NFT Lending Protocol Aggregate Borrow Volume",
        # TODO Rename as follows
        # id = "nft_lending_aggregate_borrow_volume",
        id = "nft_lending_aggregated_borrow",
        description = "A dataset of the aggregate borrow volume for different NFT lending protocols.",
        sample_questions = [
        "Plot the monthly loan volume grouped by protocol",
        "Plot a stacked bar chart of loan volume grouped by protocol since August 2022",
        "Plot top 3 protocols on April 3rd 2023",
        "Plot daily borrow volumes for each protocol in February 2023",
        "Plot monthly cumulative borrow volumes for each protocol",
        ],
    ),
    Dataset(
        name = "Growjo - Fastest Growing Companies",
        id = "growjo_fastest_growing_companies",
        description = "",
        sample_questions = [""],
    )
]
