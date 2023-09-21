import pandas as pd

from api.utils import sort_dataframe


def test_sort_by_datetime_index():
    data = {
        'name': ['B', 'A', 'C'],
    }
    df = pd.DataFrame(data, index=pd.to_datetime(['2021-09-19', '2021-09-18', '2021-09-20']))
    sorted_df = sort_dataframe(df)
    assert list(sorted_df['name']) == ['A', 'B', 'C']

def test_sort_by_date_column():
    data = {
        'name': ['A', 'B', 'C'],
        'date_column': ['2021-09-20', '2021-09-18', '2021-09-19'],
    }
    df = pd.DataFrame(data)
    sorted_df = sort_dataframe(df)
    assert list(sorted_df['name']) == ['B', 'C', 'A']

def test_sort_by_non_date():
    data = {
        'name': ['B', 'A', 'C'],
    }
    df = pd.DataFrame(data)
    sorted_df = sort_dataframe(df)
    assert list(sorted_df['name']) == ['B', 'A', 'C']

def test_sort_by_non_date_with_other_columns():
    data = {
        'name': ['B', 'A', 'C'],
        'other': ['x', 'y', 'z']
    }
    df = pd.DataFrame(data)
    sorted_df = sort_dataframe(df)
    assert list(sorted_df['name']) == ['B', 'A', 'C']
