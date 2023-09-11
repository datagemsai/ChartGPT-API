"""
API specification
"""

request = {
    "request": "Plot X",
    # By default not set, and selects most appropriate dataset from datasets available to user
    "dataset_id": "dataset_id",
    # "any" will return a list of outputs of any of the available types
    "output_type": "any",  # Or: "chart", "table", "text", "float"
    # To avoid overloading the client, we allow limiting the number of outputs
    # By default, we return 1 output
    "max_outputs": 1,
    "max_attempts": 10,
    # TBC 1 token == 1 attempt for now
    "max_tokens": 10,
    # Allow user to specify whether to stream attempts and outputs
    "stream": False,
}
# Returns "id" of job, which can be used to query status of job

response = {
    "id": "5f8b4b3a-4b0c-4b0c-8b4b-3a4b0c8b4b3a",
    "created_at": 0,
    "finished_at": 0,
    "status": "succeeded",  # Or: "failed" with errors
    "request": "Plot X",
    "dataset_id": "dataset_id",
    "attempts": [
        {
            "index": 0,
            "created_at": 0,
            "outputs": [
                {
                    "index": 0,
                    "created_at": 0,
                    "type": "chart",
                    "value": "<Plotly chart JSON string>",
                }
            ],
            "errors": [
                {
                    "index": 0,
                    "created_at": 0,
                    "type": "error_x",
                    "value": "Error message",
                }
            ],
        }
    ],
    "output_type": "any",
    # Outputs may include stdout, charts, tables, text, floats, etc.
    "outputs": [
        {
            "index": 0,
            "created_at": 0,
            "type": "chart",
            "value": "<Plotly chart JSON string>",
        }
    ],
    "errors": [
        {
            "index": 0,
            "created_at": 0,
            "type": "error_x",
            "value": "Error message",
        }
    ],
    "usage": {"tokens": 1},
}
