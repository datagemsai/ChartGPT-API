from typing import List, Union, Tuple
import pytest
from typeguard import check_type
from api.utils import clean_jupyter_shell_output
from api.chartgpt import execute_python_code
from api.prompts import CODE_GENERATION_IMPORTS
from api.types import CodeGenerationConfig, accepted_output_types, assert_matches_accepted_type
import pandas as pd


config = CodeGenerationConfig(
    max_attempts=10,
    output_type=accepted_output_types,
    output_variable="result",
)

def test_clean_jupyter_shell_output():
    assert clean_jupyter_shell_output("Out[1]:") == ""
    assert clean_jupyter_shell_output("Hello World!") == "Hello World!"
    assert clean_jupyter_shell_output("Hello World!\nOut[1]: 1") == "Hello World!\n1"
    assert clean_jupyter_shell_output("Out[1]: 1") == "1"

    assert clean_jupyter_shell_output("Out[1]:", remove_final_result=True) == ""
    assert clean_jupyter_shell_output("Hello World!", remove_final_result=True) == "Hello World!"
    assert clean_jupyter_shell_output("Hello World!\nOut[1]: 1", remove_final_result=True) == "Hello World!"
    assert clean_jupyter_shell_output("Out[1]: 1", remove_final_result=True) == ""


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
    assert result.io == "Hello World!"
    assert "df" in result.local_variables
    assert config.output_variable not in result.local_variables


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
    assert result.io == "Hello World!"
    assert config.output_variable not in result.local_variables

def test_execute_python_function_returning_string():
    code = """
def answer_question(df: pd.DataFrame) -> str:
    print("Hello World!")
    return "Hello World!"
"""
    result = execute_python_code(
        code,
        docstring="",
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": pd.DataFrame()},
        config=config,
    )
    assert result.result == "Hello World!"
    assert result.error is None
    assert result.io == "Hello World!"
    assert "df" in result.local_variables
    assert config.output_variable not in result.local_variables


def test_regression_sample_data():
    code = """
import pandas as pd
import plotly.express as px

def answer_question(df: pd.DataFrame) -> pd.DataFrame:
    print("Hello World!")
    return df

# Test the function with sample data
df_sample = pd.DataFrame({
    'protocol': ['Protocol A', 'Protocol B', 'Protocol C'],
    'total_lending_volume': [2, 2, 2]
})

answer_question(df_sample)
"""
    df = pd.DataFrame({
        'protocol': ['Protocol A', 'Protocol B', 'Protocol C'],
        'total_lending_volume': [1, 1, 1]
    })
    result = execute_python_code(
        code,
        docstring="",
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": df},
        config=config,
    )
    assert result.result is not None
    assert result.result['protocol'].tolist() == ['Protocol A', 'Protocol B', 'Protocol C']
    assert result.result['total_lending_volume'].tolist() == [1, 1, 1]
    assert result.error is None
    assert result.io == "Hello World!"
    assert config.output_variable not in result.local_variables
