from dataclasses import dataclass
from typing import Any
import pandas as pd


@dataclass
class SQLExecutionResult:
    description: str
    query: str
    dataframe: pd.DataFrame


@dataclass
class PythonExecutionResult:
    result: Any
    local_variables: dict
    io: str
    error: str


@dataclass
class QueryResult:
    description: str
    query: str
    code: str
    chart: str
    output: str
    dataframe: str
