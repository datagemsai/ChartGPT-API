from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import pandas as pd


class SQLQueryGenerationConfig:
    def __init__(self, max_attempts=10, assert_results_not_empty=True):
        self.max_attempts = max_attempts
        self.assert_results_not_empty = assert_results_not_empty


class CodeGenerationConfig:
    def __init__(self, max_attempts=10, output_type="plotly.graph_objs.Figure", output_variable="fig"):
        self.max_attempts = max_attempts
        self.output_type = output_type
        self.output_variable = output_variable


@dataclass
class SQLExecutionResult:
    description: str
    query: str
    dataframe: pd.DataFrame


@dataclass
class PythonExecutionResult:
    description: str = ""
    code: str = ""
    output: Any = None
    local_variables: Dict[str, any] = field(default_factory=dict)
    io: str = ""
    error: str = None


class OutputType(Enum):
    CHART = "chart"
    TABLE = "table"
    TEXT = "text"
    FLOAT = "float"
    INT = "int"
    BOOL = "bool"


@dataclass
class Request:
    prompt: str
    max_outputs: int
    max_attempts: int
    max_tokens: int
    stream: bool
    dataset_id: Optional[str] = None
    output_type: OutputType = OutputType.CHART


@dataclass
class Output:
    index: int
    created_at: int
    description: str
    type: str
    value: str


@dataclass
class Error:
    index: int
    created_at: int
    type: str
    value: str


@dataclass
class Attempt:
    index: int
    created_at: int
    outputs: List[Output]
    errors: List[Error]


@dataclass
class Usage:
    tokens: int


@dataclass
class Response:
    id: str
    created_at: int
    finished_at: int
    status: str
    prompt: str
    dataset_id: str
    attempts: List[Attempt]
    output_type: OutputType
    outputs: List[Output]
    errors: List[Error]
    usage: Usage


@dataclass
class QueryResult:
    output_type: OutputType
    attempts: List[Attempt]
    outputs: List[Output]
    errors: List[Error]
