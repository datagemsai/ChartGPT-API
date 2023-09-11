from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import plotly
from chartgpt_client import OutputType
from plotly.graph_objs import Figure


def map_type_to_output_type(output: Any) -> OutputType:
    if isinstance(output, bool):
        return OutputType.BOOL
    elif isinstance(output, int):
        return OutputType.INT
    elif isinstance(output, float):
        return OutputType.FLOAT
    elif isinstance(output, str):
        return OutputType.STRING
    elif isinstance(output, pd.DataFrame):
        return OutputType.PANDAS_DATAFRAME
    elif isinstance(output, Figure):
        return OutputType.PLOTLY_CHART
    else:
        raise ValueError(f"Unsupported output type: {type(output)}")


accepted_output_types = [
    # TODO Refactor this to be more structured
    plotly.graph_objs.Figure,
    pd.DataFrame,
    int,
    float,
    str,
    bool,
]


# AnyOutputType = Union[
#     List[Union[tuple(accepted_output_types)]],
#     Union[tuple(accepted_output_types)]
# ]


def matches_types(value, types: List[Any] = [Any]) -> bool:
    return any(isinstance(value, t) for t in types)


def assert_matches_accepted_type(value, types: List[Any] = [Any]) -> None:
    mismatches = []
    if isinstance(value, List):
        for index, item in enumerate(value):
            if not matches_types(item, types=types):
                mismatches.append(
                    f"Value of type {type(item)} at position {index} does not match any of the accepted output types: {accepted_output_types}"
                )
    else:
        if not matches_types(value, types=types):
            raise TypeError(
                f"Value of type {type(value)} does not match any of the accepted output types: {accepted_output_types}"
            )

    if mismatches:
        raise TypeError("\n".join(mismatches))


class SQLQueryGenerationConfig:
    def __init__(
        self,
        data_source_url: str = "",
        max_attempts=10,
        assert_results_not_empty=True,
    ):
        self.data_source_url = data_source_url
        self.max_attempts = max_attempts
        self.assert_results_not_empty = assert_results_not_empty


class CodeGenerationConfig:
    def __init__(
        self,
        max_attempts=10,
        output_type="plotly.graph_objs.Figure",
        output_variable="fig",
    ):
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
    result: Any = None
    local_variables: Dict[str, any] = field(default_factory=dict)
    io: str = ""
    error: str = None


@dataclass
class Request:
    prompt: str
    max_outputs: int
    max_attempts: int
    max_tokens: int
    stream: bool
    dataset_id: Optional[str] = None
    output_type: OutputType = OutputType.PLOTLY_CHART


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
    data_source: str
    output_type: OutputType
    attempts: List[Attempt]
    outputs: List[Output]
    errors: List[Error]
