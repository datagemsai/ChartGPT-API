# flake8: noqa

import inspect
from api.types import Role
import toml


example_query_responses = toml.load("api/example_query_responses.toml")
query_responses = [(item['query'], item['sql'], item['code']) for item in example_query_responses['query_responses']]
EXAMPLE_QUERY_RESPONSE_MESSAGES = [
    (
        {
            "role": Role.SYSTEM.value,
            "name": "example_user",
            "content": inspect.cleandoc(example_user_query),
        },
        {
            "role": Role.SYSTEM.value,
            "name": "example_sql_assistant",
            "content": inspect.cleandoc(example_sql_response),
        },
        {
            "role": Role.SYSTEM.value,
            "name": "example_code_assistant",
            "content": inspect.cleandoc(example_code_response),
        },
    ) for example_user_query, example_sql_response, example_code_response in query_responses
]
EXAMPLE_QUERY_RESPONSE_MESSAGES = [
    item for sublist in EXAMPLE_QUERY_RESPONSE_MESSAGES for item in sublist
]

SQL_QUERY_GENERATION_PROMPT_TEMPLATE = """
You are a Data Analyst specialized in GoogleSQL (BigQuery syntax), Pandas, and Plotly. Your mission is to address a specific analytics question and visualize the findings. Follow these steps:

1. **Understand the Data:** Analyze the BigQuery database schema to understand what data is available.
2. **GoogleSQL Query:** {sql_query_instruction}
3. **Python Code:** {python_code_instruction}

# GoogleSQL Guidelines
- Avoid DML operations (INSERT, UPDATE, DELETE, DROP, etc.)
- Always wrap column names in backticks: `column_name` to avoid conflicts with reserved keywords.
- Use `LOWER` for case-insensitive string comparisons: `LOWER(column_name) = LOWER('value')`
- Use `LIKE` for case-insensitive substring matches: `LOWER(column_name) LIKE '%value%'`
- If the result is empty, try `LIKE` with other variations of the value.
- Always use a `LIMIT` clause if the result is large, unless more data is requested: `LIMIT 100000`
- Always filter data for the last 3 months, unless a longer period is requested: `WHERE date >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH))`, using the appropriate date column and data type. 

# BigQuery Database Schema
The GoogleSQL query should be constructed based on the following database schema:

{database_schema}

Here are some example questions and responses:
"""
# - Always exclude NULL values: `WHERE column_name IS NOT NULL`

SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE = """
# Error Detected in GoogleSQL Query
Please correct the errors in the following SQL and try again.

Error Messages: {error_messages}

```sql
--{description}
{sql_query}
```
"""

CODE_GENERATION_IMPORTS = """
import pandas
import pandas as pd
import plotly
import plotly.express as px
import numpy as np
import networkx as nx

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
Column names: {dataframe_columns}

{dataframe_schema}

# Instructions
- Complete the following function code, replacing <COMPLETE THE FUNCTION CODE> with your own code.
- Do not try to recreate the Pandas DataFrame `df` or generate sample data.
- Always ensure the function returns a variable of the specified type.

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
Double check to make sure your answer doesn't have any functional errors, test failures, syntax errors, or omissions.

Here are some example questions and responses:
"""

CODE_GENERATION_USER_QUERY_PREFIX = """
# Analytics Question
"""

CODE_GENERATION_ERROR_PROMPT_TEMPLATE = """
# Error Detected in Python Code
Please correct the errors in the following Python code and try again.

Error Message: {error_message}

```python
'''
{description}
'''

{code}
```
"""

# Your task is to use the data provided to answer a user's Analytics Question and visualise the results.

# Instructions
# - Display text or numeric outputs using `print()`.
# - For visual outputs, use Plotly within the `answer_question()` function.

# Follow these steps:
# 1. **Understand Data:** Start by examining the GoogleSQL query to understand what data is available in the Pandas DataFrame `df`.
# 2. **Code Analysis:** Implement the function `answer_question(df: pd.DataFrame)` to analyze `df`.
# 3. **Data Visualization:** Within `answer_question(df: pd.DataFrame)`, use Plotly to create a chart that visualizes your analysis.
