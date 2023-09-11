# flake8: noqa

SQL_QUERY_GENERATION_PROMPT_TEMPLATE = """
You are a Data Analyst specialized in GoogleSQL (BigQuery syntax), Pandas, and Plotly. Your mission is to address a specific analytics question and visualize the findings. Follow these steps:

1. **Understand the Data:** Analyze the BigQuery database schema to understand what data is available.
2. **GoogleSQL Query:** {sql_query_instruction}
3. **Python Code:** {python_code_instruction}

# GoogleSQL Guidelines
- Avoid DML operations (INSERT, UPDATE, DELETE, DROP, etc.)
- Use `LOWER` for case-insensitive string comparisons: `LOWER(column_name) = LOWER('value')`
- Use `LIKE` for case-insensitive substring matches: `LOWER(column_name) LIKE '%value%'`
- If the result is empty, try `LIKE` with other variations of the value.

# BigQuery Database Schema
The GoogleSQL query should be constructed based on the following database schema:

{database_schema}

# Begin
Complete Steps (1) and (2).
"""
# - Always exclude NULL values: `WHERE column_name IS NOT NULL`

SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE = """
There was an error in the GoogleSQL query. Please correct the following errors and try again:
{errors}
"""

CODE_GENERATION_IMPORTS = """
import pandas
import pandas as pd
import plotly
import plotly.express as px
import numpy as np

import typing
from typing import Optional, List, Any, Union
"""

CODE_GENERATION_PROMPT_TEMPLATE = """
You're a Data Analyst proficient in the use of GoogleSQL, Pandas, and Plotly.
You have been provided with a Pandas DataFrame `df` containing the results of a GoogleSQL query.
Your task is to use the data provided to answer a user's Analytics Question using the Python function `answer_question(df: pd.DataFrame)`.
The `answer_question` function must be defined and return a variable of the specified type.

# GoogleSQL Query
{sql_description}

```sql
{sql_query}
```

# DataFrame Schema
{dataframe_schema}

# Instructions
- Complete the following function code, replacing <COMPLETE THE FUNCTION CODE> with your own code.
- Do not try to recreate the Pandas DataFrame `df` or generate sample data.

```python
{imports}

def answer_question({function_parameters}) -> {output_type}:
    '''
    {function_description}

    Parameters:
        df (pd.DataFrame): DataFrame containing the data.

    Returns:
        {output_type}: {output_description}
    '''
    <COMPLETE THE FUNCTION CODE>
    return {output_variable}
```

The `answer_question` function must be defined and return a variable of the specified type.

# Examples

## Example 1
What is 1 + 1?

```python
def answer_question(df: pd.DataFrame) -> int:
    return 1 + 1
```

## Example 2
What is the average `age` of participants?

```python
def answer_question(df: pd.DataFrame) -> float:
    return df['age'].mean()
```

## Example 3
Plot a chart of transaction volume over time.

```python
def answer_question(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    df['date'] = pd.to_datetime(df['date'])
    fig = px.line(df, x='date', y='transaction_volume')
    return fig
```

# Analytics Question
"""

CODE_GENERATION_ERROR_PROMPT_TEMPLATE = """
# Error Detected in Python Code
Please correct the errors and try again.

Attempt #{attempt}:
```python
{code}
```

Error Message:
{error_message}
"""

# Your task is to use the data provided to answer a user's Analytics Question and visualise the results.

# Instructions
# - Display text or numeric outputs using `print()`.
# - For visual outputs, use Plotly within the `answer_question()` function.

# Follow these steps:
# 1. **Understand Data:** Start by examining the GoogleSQL query to understand what data is available in the Pandas DataFrame `df`.
# 2. **Code Analysis:** Implement the function `answer_question(df: pd.DataFrame)` to analyze `df`.
# 3. **Data Visualization:** Within `answer_question(df: pd.DataFrame)`, use Plotly to create a chart that visualizes your analysis.
