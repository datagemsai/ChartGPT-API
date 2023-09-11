from typing import List, Tuple, Union

import pandas as pd
from typeguard import check_type

from api.chartgpt import execute_python_code
from api.templates import CODE_GENERATION_IMPORTS
from api.types import (AnyOutputType, CodeGenerationConfig,
                       accepted_output_types)

config = CodeGenerationConfig(
    max_attempts=10,
    output_type=AnyOutputType,
    output_variable="result",
)


def test_execute_python_code():
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
    #     code = """
    # import pandas as pd

    # # Return results
    # # [pd.Series([1, 2, 3]), 1, "A", 1.0, False]
    # pd.Series([1, 2, 3])
    # """
    #     result = execute_python_code(
    #         code,
    #         docstring="",
    #         imports=CODE_GENERATION_IMPORTS,
    #         local_variables={"df": pd.DataFrame()},
    #         config=config,
    #     )
    # assert result.result == 2
    # assert result.error is None
    # assert result.io == "Hello World!\nOut[2]: 2\n"
    # assert "df" in result.local_variables

    result = pd.Series([1, 2, 3])

    def matches_accepted_type(value):
        return any(isinstance(value, t) for t in accepted_output_types)

    mismatches = []
    if isinstance(result, List):
        for index, item in enumerate(result):
            if not matches_accepted_type(item):
                mismatches.append(
                    f"Value of type {type(item)} at position {index} does not match any of the accepted output types: {accepted_output_types}"
                )
    else:
        if not matches_accepted_type(result):
            raise TypeError(
                f"Value of type {type(result)} does not match any of the accepted output types: {accepted_output_types}"
            )

    if mismatches:
        raise TypeError("\n".join(mismatches))
