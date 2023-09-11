import ast
import inspect
from dataclasses import dataclass

import pytest

from chartgpt.tools.python.secure_ast import secure_eval, secure_exec


@dataclass
class Test:
    _private = 1
    __private__ = 1


case_throwaway_variable = inspect.cleandoc(
    """
for _ in range(10):
    pass
"""
)

case_local_private_variable = inspect.cleandoc(
    """
_private = 1
"""
)

case_class_private_variable_access = inspect.cleandoc(
    """
import pandas as pd

pd._config
pd.__version__

from google.cloud.bigquery import Client

bigquery_client = Client()
print(bigquery_client._credentials.token)
"""
)


def test_throwaway_variable():
    secure_exec(code=case_throwaway_variable)


def test_local_private_variable():
    secure_exec(code=case_local_private_variable)


def test_class_private_variable_access():
    with pytest.raises(ValueError):
        secure_exec(code=case_class_private_variable_access)
