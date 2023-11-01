import json
import pprint
import re  # noqa: F401
from aenum import Enum, no_arg


class OutputType(str, Enum):
    """
    The output type of the response.
    """

    """
    allowed enum values
    """
    ANY = 'any'
    INT = 'int'
    FLOAT = 'float'
    STRING = 'string'
    BOOL = 'bool'
    PLOTLY_CHART = 'plotly_chart'
    PANDAS_DATAFRAME = 'pandas_dataframe'
    SQL_QUERY = 'sql_query'
    PYTHON_CODE = 'python_code'
    PYTHON_OUTPUT = 'python_output'

    @classmethod
    def from_json(cls, json_str: str) -> OutputType:
        """Create an instance of OutputType from a JSON string"""
        return OutputType(json.loads(json_str))
