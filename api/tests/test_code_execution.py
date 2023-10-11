import json

import pandas as pd
import plotly.graph_objects as go
import pytest

from api import utils
from api.chartgpt import execute_python_code
from api.prompts import CODE_GENERATION_IMPORTS
from api.types import (CodeGenerationConfig, accepted_output_types,
                       assert_matches_accepted_type)
from api.utils import clean_jupyter_shell_output

config = CodeGenerationConfig(
    max_attempts=10,
    output_types=accepted_output_types,
    output_variable="result",
)


code_test_cases = [
"""
def answer_question(df):
    return 1
"""
]


class TestCases:
    @pytest.mark.parametrize(
        "code",
        code_test_cases,
    )
    @pytest.mark.asyncio
    async def test_execute_code_test_cases(self, code):
        result = await execute_python_code(
            code,
            docstring="",
            imports=CODE_GENERATION_IMPORTS,
            local_variables={},
            config=config,
        )
        assert result.result is not None
        assert result.error is None
        assert result.io == ""
        assert config.output_variable not in result.local_variables


def test_clean_jupyter_shell_output():
    assert clean_jupyter_shell_output("Out[1]:") == ""
    assert clean_jupyter_shell_output("Hello World!") == "Hello World!"
    assert clean_jupyter_shell_output("Hello World!\nOut[1]: 1") == "Hello World!\n1"
    assert clean_jupyter_shell_output("Out[1]: 1") == "1"

    assert clean_jupyter_shell_output("Out[1]:", remove_final_result=True) == ""
    assert (
        clean_jupyter_shell_output("Hello World!", remove_final_result=True)
        == "Hello World!"
    )
    assert (
        clean_jupyter_shell_output("Hello World!\nOut[1]: 1", remove_final_result=True)
        == "Hello World!"
    )
    assert clean_jupyter_shell_output("Out[1]: 1", remove_final_result=True) == ""


@pytest.mark.asyncio
async def test_execute_python_function():
    code = """
def answer_question(df: pd.DataFrame) -> int:
    print("Hello World!")
    return 1 + 1
"""
    result = await execute_python_code(
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


@pytest.mark.asyncio
async def test_execute_python_code():
    code = """
print("Hello World!")
1 + 1
"""
    result = await execute_python_code(
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


@pytest.mark.asyncio
async def test_execute_python_function_returning_string():
    code = """
def answer_question(df: pd.DataFrame) -> str:
    print("Hello World, printed!")
    return "Hello World, returned!"
"""
    result = await execute_python_code(
        code,
        docstring="",
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": pd.DataFrame()},
        config=config,
    )
    assert result.result == "Hello World, returned!"
    assert result.error is None
    assert result.io == "Hello World, printed!"
    assert "df" in result.local_variables
    assert config.output_variable not in result.local_variables


@pytest.mark.asyncio
async def test_regression_sample_data():
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
    df = pd.DataFrame(
        {
            "protocol": ["Protocol A", "Protocol B", "Protocol C"],
            "total_lending_volume": [1, 1, 1],
        }
    )
    result = await execute_python_code(
        code,
        docstring="",
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": df},
        config=config,
    )
    assert result.result is not None
    assert result.result["protocol"].tolist() == [
        "Protocol A",
        "Protocol B",
        "Protocol C",
    ]
    assert result.result["total_lending_volume"].tolist() == [1, 1, 1]
    assert result.error is None
    assert result.io == "Hello World!"
    assert config.output_variable not in result.local_variables


@pytest.mark.asyncio
async def test_utils_json_encoder_period():
    code = """
import pandas as pd
import plotly.express as px

def answer_question(df: pd.DataFrame):
    # Convert the 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Group by month and calculate the average APR
    df_grouped = df.groupby(df['date'].dt.to_period('M')).mean()

    # Plot the average APR over time
    fig = px.line(df_grouped, x=df_grouped.index, y='apr', title='Average APR for ***REMOVED*** protocol in the past 6 months')
    return fig

answer_question(df)
"""
    df = pd.DataFrame(
        {
            "apr": [0, 0, 0],
            "date": ["2021-01-01", "2021-02-01", "2021-03-01"],
        }
    )
    result = await execute_python_code(
        code,
        docstring="",
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": df},
        config=config,
    )
    fig = result.result
    fig = json.dumps(fig, cls=utils.CustomPlotlyJSONEncoder)

    # Check that Period types are successfully encoded
    # Avoids error "OverflowError: Maximum recursion level reached"
    df["date"] = pd.to_datetime(df["date"])
    df["date_periods"] = df["date"].dt.to_period("M")
    # df = utils.convert_period_dtype_to_timestamp(df)
    df.to_json(orient="records", default_handler=str)


@pytest.mark.asyncio
async def test_utils_json_encoder_interval():
    code = """
import pandas as pd
import plotly.express as px

def answer_question(df: pd.DataFrame):
    fig = px.bar(df, x='x', y='y')
    return fig
"""
    data = {
        'x': [pd.Interval(0, 1, closed='right')],
        'y': [1]
    }
    df = pd.DataFrame(data)
    result = await execute_python_code(
        code,
        docstring="",
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": df},
        config=config,
    )
    assert result.error is None
    assert result.result is not None
    fig_json_string = json.dumps(result.result, cls=utils.CustomPlotlyJSONEncoder)
    fig_json = json.loads(fig_json_string)
    _ = go.Figure(fig_json)


@pytest.mark.asyncio
async def test_dataframe_index_mutation():
    """
    When the function is called twice, check that the index of the dataframe is not mutated.
    """
    code = """
import pandas as pd
import plotly.express as px

def answer_question(df: pd.DataFrame):
    # Convert the 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Set 'date' as the index
    df.set_index('date', inplace=True)
    
    # Resample the data to get the average APR for each month
    monthly_avg_apr = df['apr'].resample('M').mean()
    
    # Reset the index
    monthly_avg_apr = monthly_avg_apr.reset_index()
    
    # Plot the average APR over time
    fig = px.line(monthly_avg_apr, x='date', y='apr', title='Average APR for ***REMOVED*** Protocol Over the Past 6 Months')
    
    return fig

answer_question(df)
"""
    df = pd.DataFrame(
        {
            "apr": [0, 0, 0],
            "date": ["2021-01-01", "2021-02-01", "2021-03-01"],
        }
    )
    result = await execute_python_code(
        code,
        docstring="",
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": df.copy()},
        config=config,
    )
    assert not result.error
