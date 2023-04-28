"""A tool for running python code in a REPL."""

import ast
import sys
from io import StringIO
from typing import Dict, Optional
import re
from collections.abc import Callable
from pydantic import Field, root_validator
from analytics_bot_langchain.tools.python.secure_ast import secure_eval, secure_exec
import streamlit as st

from langchain.tools.base import BaseTool
from langchain.utilities import PythonREPL


def _get_default_python_repl() -> PythonREPL:
    return PythonREPL(_globals=globals(), _locals=None)


class PythonAstREPLTool(BaseTool):
    """A tool for running python code in a REPL."""

    name = "python_repl_ast"
    description = (
        "A Python shell. Use this to execute python commands. "
        "Input should be a valid python command. "
        "When using this tool, sometimes output is abbreviated - "
        "make sure it does not look abbreviated before using it in your answer."
    )
    globals: Optional[Dict] = Field(default_factory=dict)
    locals: Optional[Dict] = Field(default_factory=dict)
    sanitize_input: bool = True
    query_post_processing: Optional[Callable[[str], str]] = None

    @root_validator(pre=True, allow_reuse=True)
    def validate_python_version(cls, values: Dict) -> Dict:
        """Validate valid python version."""
        if sys.version_info < (3, 9):
            raise ValueError(
                "This tool relies on Python 3.9 or higher "
                "(as it uses new functionality in the `ast` module, "
                f"you have Python version: {sys.version}"
            )
        return values

    def _run(self, query: str) -> str:
        """Use the tool."""
        try:
            if self.sanitize_input:
                # Remove the triple backticks from the query.
                query = query.strip().removeprefix("```python")
                query = query.strip().strip("```")
            if self.query_post_processing:
                query = self.query_post_processing(query)

            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            
            try:
                secure_exec(ast.unparse(module), custom_globals=self.globals, custom_locals=self.locals)  # type: ignore
            except ValueError as e:
                st.error(e)
                return "Stop"
            
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            try:
                output = secure_eval(module_end_str, custom_globals=self.globals, custom_locals=self.locals)
            except Exception:
                old_stdout = sys.stdout
                sys.stdout = mystdout = StringIO()
                try:
                    secure_exec(module_end_str, custom_globals=self.globals, custom_locals=self.locals)
                    sys.stdout = old_stdout
                    output = mystdout.getvalue()
                except ValueError as e:
                    st.error(e)
                    return "Stop"
                except Exception as e:
                    sys.stdout = old_stdout
                    output = str(e)
            return output
        except Exception as e:
            return "{}: {}".format(type(e).__name__, str(e))

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("PythonReplTool does not support async")
