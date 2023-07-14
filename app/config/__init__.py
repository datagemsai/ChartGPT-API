from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Dataset:
    name: str
    id: str
    description: str
    sample_questions: List[str]
    tables: List[str] = field(default_factory=lambda: [])

    def __repr__(self):
        return self.name
 
    def __eq__(self, other) -> bool:
        return self.id == other.id
