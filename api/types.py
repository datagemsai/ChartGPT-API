from dataclasses import dataclass, field
from typing import Any, Dict
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


@dataclass
class QueryResult:
    description: str
    query: str
    code: str
    chart: str
    output: str
    dataframe: str
