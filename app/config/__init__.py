from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Dataset:
    name: str
    id: str
    description: str
    sample_questions: List[str]
    tables: List[str] = field(default_factory=lambda: [])
    column_descriptions: dict = field(default_factory=lambda: {})
    """
    TODO In future can be automated using LLM:
    
    "For each column in the dataset, provide a brief description
    including which unique protocols this column applies to
    by checking for protocols where the values are all null.
    Construct and print a dictionary where the key is the column name,
    and the value is the description, for example:
    "principal_amount": "This is the principal amount of the loan. Not relevant for jpegd and bend protocols".
    Do not limit the number of rows in the SQL query.
    Provide a unique description for each column based on what you can see."
    """

    def __repr__(self):
        return self.name

    def __eq__(self, other) -> bool:
        return self.id == other.id
