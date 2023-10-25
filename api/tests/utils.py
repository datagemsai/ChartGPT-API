import os
import json
import sqlparse
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

import chartgpt_client


def display_and_save_chart_output(output_value: str, output_directory: Path, output_filename: str = "chart.png") -> None:
    figure_json = json.loads(output_value, strict=False)
    fig = go.Figure(figure_json)
    os.makedirs(output_directory, exist_ok=True)
    fig.write_image(Path.joinpath(output_directory, output_filename))
    fig.show()


def display_and_save_text_output(output_value: str, output_directory: Path, output_filename: str = "code.py") -> None:
    os.makedirs(output_directory, exist_ok=True)
    with open(Path.joinpath(output_directory, output_filename), mode='w') as f:
        f.write(output_value)
    print(output_value)


def display_and_save_dataframe_output(output_value: str, output_directory: Path, output_filename: str = "dataframe.csv") -> None:
    df = pd.read_json(output_value)
    os.makedirs(output_directory, exist_ok=True)
    df.to_csv(Path.joinpath(output_directory, output_filename))
    print(df)


def display_and_save_response_results(response: chartgpt_client.Response, output_directory: Path) -> None:
    for attempt in response.attempts:
        for output in attempt.outputs:
            print(f"Processing attempt of type {output.type}")
            if output.type == chartgpt_client.OutputType.PLOTLY_CHART.value:
                display_and_save_chart_output(
                    output_value=output.value,
                    output_directory=output_directory,
                    output_filename=f"chart_attempt_{attempt.index}.png"
                )
            elif output.type == chartgpt_client.OutputType.PYTHON_CODE.value:
                display_and_save_text_output(
                    output_value=output.value,
                    output_directory=output_directory,
                    output_filename=f"code_attempt_{attempt.index}.py"
                )
            elif output.type == chartgpt_client.OutputType.SQL_QUERY.value:
                display_and_save_text_output(
                    output_value=sqlparse.format(output.value, reindent=True, keyword_case='upper'),
                    output_directory=output_directory,
                    output_filename=f"query_attempt_{attempt.index}.sql"
                )
            elif output.type == chartgpt_client.OutputType.PANDAS_DATAFRAME.value:
                display_and_save_dataframe_output(
                    output_value=output.value,
                    output_directory=output_directory,
                    output_filename=f"dataframe_attempt_{attempt.index}.csv"
                )
        for error in attempt.errors:
            print(error)

    for output in response.outputs:
        print(f"Processing output of type {output.type}")
        if output.type in [
            chartgpt_client.OutputType.PYTHON_OUTPUT.value,
            chartgpt_client.OutputType.INT.value,
            chartgpt_client.OutputType.FLOAT.value,
            chartgpt_client.OutputType.STRING.value,
        ]:
            print(output.value)
        elif output.type == chartgpt_client.OutputType.PLOTLY_CHART.value:
            display_and_save_chart_output(
                output_value=output.value,
                output_directory=output_directory,
                output_filename=f"chart_{output.index}.png"
            )
        elif output.type == chartgpt_client.OutputType.PYTHON_CODE.value:
            display_and_save_text_output(
                output_value=output.value,
                output_directory=output_directory,
                output_filename=f"code_{output.index}.py"
            )
        elif output.type == chartgpt_client.OutputType.SQL_QUERY.value:
            display_and_save_text_output(
                output_value=sqlparse.format(output.value, reindent=True, keyword_case='upper'),
                output_directory=output_directory,
                output_filename=f"query_{output.index}.sql"
            )
        elif output.type == chartgpt_client.OutputType.PANDAS_DATAFRAME.value:
            display_and_save_dataframe_output(
                output_value=output.value,
                output_directory=output_directory,
                output_filename=f"dataframe_{output.index}.csv"
            )
