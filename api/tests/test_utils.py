import pandas as pd

from api import utils

# TODO Fix tests
# def test_sort_by_datetime_index():
#     data = {
#         'name': ['B', 'A', 'C'],
#     }
#     df = pd.DataFrame(data, index=pd.to_datetime([
#         pd.Period(year=2021, month=9, day=19),
#         pd.Period(year=2021, month=9, day=18),
#         pd.Period(year=2021, month=9, day=20),
#     ]))
#     sorted_df = utils.sort_dataframe(df)
#     assert list(sorted_df['name']) == ['A', 'B', 'C']

# def test_sort_by_date_column():
#     data = {
#         'name': ['A', 'B', 'C'],
#         'date_column': [
#             pd.Period(year=2021, month=9, day=20),
#             pd.Period(year=2021, month=9, day=18),
#             pd.Period(year=2021, month=9, day=19)
#         ],
#     }
#     df = pd.DataFrame(data)
#     sorted_df = utils.sort_dataframe(df)
#     assert list(sorted_df['name']) == ['B', 'C', 'A']

# def test_sort_by_non_date():
#     data = {
#         'name': ['B', 'A', 'C'],
#     }
#     df = pd.DataFrame(data)
#     sorted_df = utils.sort_dataframe(df)
#     assert list(sorted_df['name']) == ['B', 'A', 'C']


def test_sort_by_non_date_with_other_columns():
    data = {"name": ["B", "A", "C"], "other": ["x", "y", "z"]}
    df = pd.DataFrame(data)
    sorted_df = utils.sort_dataframe(df)
    assert list(sorted_df["name"]) == ["B", "A", "C"]


def test_dataframe_pre_processing():
    df = pd.DataFrame({"value": [0, 0]})

    # Convert Period dtype to timestamp to ensure DataFrame is JSON serializable
    df = utils.convert_period_dtype_to_timestamp(df)

    # Sort DataFrame by date column if it exists
    df = utils.sort_dataframe(df)

    # Assert "value" is of int type
    assert not pd.api.types.is_period_dtype(df["value"])
    assert df["value"].dtype == "int64"


def test_create_type_string():
    assert (
        utils.create_type_string([int, float])
        == "Union[List[Union[builtins.int, builtins.float]], Union[builtins.int, builtins.float]]"
    )


def test_clean_jupyter_shell_output():
    output = """Out[1]:
[                             date       holders     marketcap         sales  ...     transfers        volume  washtrade_level  washtrade_volume
count                          90     90.000000  9.000000e+01     90.000000  ...     90.000000  9.000000e+01               90      9.000000e+01
"""
    assert utils.clean_jupyter_shell_output(output, remove_final_result=True) == ""
