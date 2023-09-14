from dataclasses import dataclass, field
import enum
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy

import pandas as pd
import plotly
from chartgpt_client import OutputType
from plotly.graph_objs import Figure


def map_type_to_output_type(output: Any) -> OutputType:
    if isinstance(output, bool):
        return OutputType.BOOL
    elif isinstance(output, numpy.bool_):
        return OutputType.BOOL
    elif isinstance(output, int):
        return OutputType.INT
    elif isinstance(output, numpy.int64):
        return OutputType.INT
    elif isinstance(output, float):
        return OutputType.FLOAT
    elif isinstance(output, numpy.float64):
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
    numpy.int64,
    float,
    numpy.float64,
    str,
    bool,
    numpy.bool_,
]


def matches_types(value, types: List[Any] = [Any]) -> bool:
    return any(isinstance(value, t) for t in types)


def assert_matches_accepted_type(value, types: List[Any] = [Any]) -> None:
    mismatches = []
    if isinstance(value, List) or isinstance(value, Tuple):
        for index, item in enumerate(value):
            if not matches_types(item, types=types):
                mismatches.append(
                    f"Value of type {type(item)} at position {index} does not match any of the accepted output types: {types}"
                )
    elif isinstance(value, dict):
        for key, item in value.items():
            if not matches_types(item, types=types):
                mismatches.append(
                    f"Value of type {type(item)} at key {key} does not match any of the accepted output types: {types}"
                )
    else:
        if not matches_types(value, types=types):
            raise TypeError(
                f"Value of type {type(value)} does not match any of the accepted output types: {types}"
            )

    if mismatches:
        raise TypeError("\n".join(mismatches))


class Role(enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Message:
    id: Optional[str]
    created_at: Optional[int]
    content: str
    role: Role

    def to_json(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "content": self.content,
            "role": self.role.value,
        }


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
    messages: List[Message]


@dataclass
class PythonExecutionResult:
    description: str = ""
    code: str = ""
    result: Any = None
    local_variables: Dict[str, any] = field(default_factory=dict)
    io: str = ""
    error: str = None
    messages: List[Message] = field(default_factory=list)


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
