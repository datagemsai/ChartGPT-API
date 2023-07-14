"""A tool for running python code in a REPL."""

import ast
import sys
from io import StringIO
from typing import Dict, Optional
from collections.abc import Callable
from pydantic import Field, root_validator
from chartgpt.tools.python.secure_ast import secure_eval, secure_exec
import streamlit as st
from langchain.tools.base import BaseTool
import app
import re
from contextlib import redirect_stdout
from io import StringIO
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)


def sanitize_input(query: str) -> str:
    """Sanitize input to the python REPL.
    Remove whitespace, backtick & python (if llm mistakes python console as terminal)

    Args:
        query: The query to sanitize

    Returns:
        str: The sanitized query
    """

    # Removes `, whitespace & python from start
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query


class PythonAstREPLTool(BaseTool):
    """A tool for running python code in a REPL."""

    name = "python_repl_ast"
    description = (
        "A Python shell. Use this to execute python commands including: BigQuery queries, Pandas analytics, Plotly charts. "
        "Input should be a valid python command. "
        "When using this tool, sometimes output is abbreviated - "
        "make sure it does not look abbreviated before using it in your answer."
    )
    locals: Optional[Dict] = Field(default_factory=dict)
    globals: Optional[Dict] = Field(default_factory=dict)
    sanitize_input: bool = True
    query_post_processing: Optional[Callable[[str], str]] = None
    secure_execution: bool = True

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

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        try:
            if self.sanitize_input:
                query = sanitize_input(query)
            if self.query_post_processing:
                query = self.query_post_processing(query)
            self.globals = self.locals
            app.logger.info("Executing `exec(ast.unparse(module), self.globals, self.locals)`")
            app.logger.info("Raw query:\n\n%s", query)
            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            app.logger.info(ast.unparse(module))
            if self.secure_execution:
                secure_exec(ast.unparse(module), custom_globals=self.globals, custom_locals=self.locals)
            else:
                exec(ast.unparse(module), self.globals, self.locals)  # type: ignore
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            io_buffer = StringIO()
            try:
                with redirect_stdout(io_buffer):
                    app.logger.info("Executing `eval(module_end_str, self.globals, self.locals)`")
                    app.logger.info(module_end_str)
                    if self.secure_execution:
                        ret = secure_eval(module_end_str, custom_globals=self.globals, custom_locals=self.locals)
                    else:
                        ret = eval(module_end_str, self.globals, self.locals)
                    if ret is None:
                        return io_buffer.getvalue()
                    else:
                        return ret
            except Exception as e:
                app.logger.info(e)
                with redirect_stdout(io_buffer):
                    app.logger.info("Executing `eval(module_end_str, self.globals, self.locals)`")
                    app.logger.info(module_end_str)
                    if self.secure_execution:
                        secure_exec(module_end_str, custom_globals=self.globals, custom_locals=self.locals)
                    else:
                        exec(module_end_str, self.globals, self.locals)
                return io_buffer.getvalue()
        except Exception as e:
            app.logger.info(e)
            return "{}: {}".format(type(e).__name__, str(e))
        finally:
            # Clear Streamlit output and start on new line
            st.session_state["container"].text("")
            st.session_state["text"] = "\n\n"
            st.session_state["empty_container"] = st.session_state["container"].empty()

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("PythonAstReplTool does not support async")
