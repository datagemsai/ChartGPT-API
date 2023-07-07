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

@dataclass
class Table:
    name: str
    description: str
    sample_questions: List[str]

    project_id: str
    dataset_id: str
    table_id: str

    @property
    def dataset_uid(self) -> str:
        return self.project_id + "." + self.dataset_id

    @property
    def table_uid(self) -> str:
        return self.project_id + "." + self.dataset_id + "." + self.table_id

    def __repr__(self):
        return self.name
