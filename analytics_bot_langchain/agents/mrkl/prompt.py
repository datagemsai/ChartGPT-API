# flake8: noqa
PREFIX = """Answer the following questions as best you can. You have access to the python_repl_ast tool:"""
FORMAT_INSTRUCTIONS = """
# Formatting Instructions
```python
# Thought: <your thought>
<Python code>
```

Observation: <Python code output>

... (this Code / Observation pattern can repeat N times)

Final Answer: <the final answer to the original input question>

## Example:
```python
# Thought: I think the answer is 42.
print(data)
```

Observation: 42

Final Answer: 42
"""
SUFFIX = """Begin!

Question: {input}
{agent_scratchpad}"""
