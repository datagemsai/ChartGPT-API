"""Custom exceptions for the ChartGPT API."""

class ContextLengthError(Exception):
    """Raised when the maximum LLM context length is exceeded."""

class MaxAttemptsError(Exception):
    """Raised when the maximum number of output attempts is exceeded."""

class MaxOutputsError(Exception):
    """Raised when the maximum number of outputs generated is exceeded."""

class MaxTokensError(Exception):
    """Raised when the maximum number of tokens used is exceeded."""

class SQLValidationError(Exception):
    """Raised when there is an error validating SQL query returned from LLM."""

class PythonExecutionError(Exception):
    """Raised when there is an error executing Python code returned from LLM."""

class InsecureRequestError(Exception):
    """Raised when a user's request is considered insecure."""
