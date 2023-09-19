from typing import List, Union, Tuple
import pytest
from typeguard import check_type
from api.chartgpt import execute_python_code
from api.prompts import CODE_GENERATION_IMPORTS
from api.types import CodeGenerationConfig, accepted_output_types, assert_matches_accepted_type
import pandas as pd


config = CodeGenerationConfig(
    max_attempts=10,
    output_type=accepted_output_types,
    output_variable="result",
)

def test_execute_python_function():
    code = """
def answer_question(df: pd.DataFrame) -> int:
    print("Hello World!")
    return 1 + 1
"""
    result = execute_python_code(
        code,
        docstring="",
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": pd.DataFrame()},
        config=config,
    )
    assert result.result == 2
    assert result.error is None
    assert result.io == "Hello World!\nOut[2]: 2\n"
    assert "df" in result.local_variables
    # TODO The output_variable is no longer used in the code generation
    # assert config.output_variable in result.local_variables


def test_unexpected_output_type():
    result = pd.Series([1, 2, 3])
    with pytest.raises(TypeError):
        assert_matches_accepted_type(result, accepted_output_types)


def test_execute_python_code():
    code = """
print("Hello World!")
1 + 1
"""
    result = execute_python_code(
        code,
        docstring="",
        imports=CODE_GENERATION_IMPORTS,
        local_variables={},
        config=config,
    )
    assert result.result == 2
    assert result.error is None
    assert result.io == "Hello World!\nOut[1]: 2\n"
    # assert "df" in result.local_variables
