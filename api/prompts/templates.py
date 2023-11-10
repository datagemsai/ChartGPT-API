# flake8: noqa

from dataclasses import dataclass
from typing import Dict, List
import toml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import inspect
from api.types import Role
import toml


@dataclass
class Example:
    data_source_url: str
    query: str
    sql: str
    code: str


examples_generated = [
    Example(**item)
    for item in toml.load("api/prompts/examples/examples_generated.toml")['examples']
]


def get_relevant_examples(query, data_source_url=None, examples=examples_generated) -> List[Example]:
    """
    Get top 5 relevant examples for a specific data source,
    or from all examples if no data source is specified,
    using cosine similarity of question.
    """
    # If data source is specified, filter examples by it
    if data_source_url:
        filtered_examples = [example for example in examples if not example.data_source_url or example.data_source_url == data_source_url]
    
    # If examples are empty after filtering, use all examples
    if not filtered_examples:
        filtered_examples = examples

    # Extract queries from examples
    example_queries = [example.query for example in filtered_examples]
    
    # Combine the new query with example queries
    texts = example_queries + [query]
    
    # Convert the queries to TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Compute cosine similarity between the new query and each example
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    # Get indices of the top 5 most similar examples
    relevant_indices = cosine_similarities.argsort()[0][-5:][::-1]
    
    return [filtered_examples[i] for i in relevant_indices]


def convert_examples_to_llm_messages(
        examples: List[Example],
        include_sql_query=True,
        include_code=True
    ) -> List[Dict]:
    """
    Convert a list of examples to a list of LLM messages.
    """
    messages = []
    for example in examples:
        messages.append(
            {
                "role": Role.SYSTEM.value,
                "name": "example_user",
                "content": inspect.cleandoc(example.query),
            }
        )
        if include_sql_query:
            messages.append(
                {
                    "role": Role.SYSTEM.value,
                    "name": "example_sql_assistant",
                    "content": inspect.cleandoc(example.sql),
                }
            )
        if include_code:
            messages.append(
                {
                    "role": Role.SYSTEM.value,
                    "name": "example_code_assistant",
                    "content": inspect.cleandoc(example.code),
                }
            )
    return messages


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
- Always filter data for the last 3 months, unless a longer period is requested: `WHERE `date_column` >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH))`, using the appropriate date column and data type. 
- If the filtered results are empty, try replacing `CURRENT_DATE()` with `(SELECT MAX(`date_column`) FROM `table_name`)`.

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
import numpy
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
