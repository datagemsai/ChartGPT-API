# flake8: noqa
PREFIX = """Answer the following questions as best you can. You have access to the python_repl_ast tool:"""

FORMAT_INSTRUCTIONS = """
# Formatting Instructions

Always start your response with an appropriate prefix from the following list: [Thought, Action Input, Observation]
Never respond without an Action Input.

Question: {input}
Thought: <consider what to do>
Action Input:
```python
<Python code>
```
Observation: <result of the action>

... (Repeat Thought/Action Input/Observation pattern as needed to answer the question)

Analysis complete: <answer to the original input question>
Analysis failed: <failure message if an answer couldn't be found>
"""

SUFFIX = """Begin!

Question: {input}
Thought: {agent_scratchpad}"""
