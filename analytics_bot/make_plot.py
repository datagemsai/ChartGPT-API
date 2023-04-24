
import io
from typing import List
from matplotlib import pyplot as plt
import pandas as pd
import inspect

from analytics_bot.base import completion, pyplot_preamble, plotly_preamble, PlotResult, pyplot_exec_prefix, fix_python_bug


def chart_completion(question, result, tables_summary, plot_lib='matplotlib'):
    question = question.strip()

    result = result[:1]
    # print(f"TABLE INPUT TO PROMPT: \n{result}\n\n\n")
    if plot_lib == 'plotly':
        # prompt = f""" records_df = pd.DataFrame.from_records({result})\n
        # As a world class expert software engineer and data scientist, given the above dataset, write a
        # detailed and correct plotly code to produce a chart as requested:\n
        # "{question}"
        # \nComment the code with your logic. Use fig.show() to display the plot at the end.
        # Remember that you need to add axes names, units, legend. Update the layout accordingly for good visualization
        # including colors.
        # """ + plotly_preamble
        #        prompt = f""" {tables_summary}\n
        #                As a world class expert software engineer and data scientist, given the above dataset, write a
        #                detailed and correct plotly code to produce a chart as requested:\n
        #                "{question}"
        #                \nUse fig.show() to display the plot at the end. Do not forget to filter by dates if requested.
        #                Add axes names, units, legend. Update the layout accordingly for color-coded visualizations.
        #                Keep code as succinct as possible and do not add comments.
        # ```
        # """ + plotly_preamble
        prompt = f""" 
records_df = pd.DataFrame.from_records({result})\n
As a world class expert software engineer and data scientist, given the above dataset, write a
detailed and correct plotly code to produce a chart as requested:\n
"{question}"
\nUse st.plotly_chart(fig, use_container_width=True) to display the plot at the end. 
Add axes names, units, legend. Update the layout accordingly. 
Keep code as succinct as possible and do not add comments.
```
""" + plotly_preamble
        # Do not forget to filter by dates if requested.
        # for color-coded visualizations
        # including colors
        # When requested for distributions, you should group by the object.
        # Comment the code with your logic.
        # When requested for distributions you should group by the object and not plot across time (where time column can be date, day, dt, block_time [...]).

    else:
        prompt = f"""
records_df = pd.DataFrame.from_records({result})


As a senior analyst, given the above data set, write detailed and correct matplotlib code to produce a chart as requested:

"{question}"

Comment the code with your logic. Use plt.show() to display the plot at the end.

```
        """ + pyplot_preamble
    # print(prompt)
    prompt = inspect.cleandoc(prompt)
    resp = completion(prompt)
    return resp


def get_plot_result(py: str, data):
    """
    Executes a Python script to generate a plot based on the provided data.

    Args:
        py: The Python script to execute.
        data: The data to use when generating the plot.

    Returns:
        A PlotResult instance with the Python script, plot image, and any errors encountered.
    """
    print(py)
    error = None
    buf = io.BytesIO()
    result = None

    def get_data():
        """
        Helper function to load the data into a pandas DataFrame.
        """
        return pd.DataFrame.from_records(data)

    try:
        exec(py, {"get_data": get_data})  # Execute the Python script with the data
        print(f"[DEBUG]: INPUT DATA TO BOT: \n{get_data()}")  # Debug print of the input data

        plt.savefig(buf, format="png")  # Save the plot image
        buf.seek(0)  # Move the buffer pointer to the beginning of the buffer
    except Exception as e:
        import traceback

        error = traceback.format_exc()  # Record the error message
        print(error)

    # Return a PlotResult instance with the Python script, plot image, and any errors encountered
    return PlotResult(python=py, result=buf, error=error)


def plot_completion_pipeline(completions: List, data: List, query_fixes=None, plot_lib='matplotlib', max_retries=5) -> PlotResult:
    """
    Given a list of code completions and a dataset, attempts to create a plot using the provided code.
    If the plot creation fails, attempts to fix the code by calling `fix_python_bug()` and retry up to `max_retries`
    times before raising an error.

    Args:
        completions: A list of suggested code completions.
        data: A list of dictionaries, each representing a row of data to be plotted.
        query_fixes: A list of corrected Python code.
        plot_lib: A string representing the plotting library to be used. Defaults to 'matplotlib'.
        max_retries: Maximum number of attempts to fix the code before raising an error. Defaults to 5.

    Returns:
        A PlotResult instance with the resulting plot or an error message.
    """
    if query_fixes is None:
        query_fixes = []

    for completion in completions:
        py = completion
        py = py.split("```")[0]

        if plot_lib == 'matplotlib':
            py = pyplot_preamble + pyplot_exec_prefix + py
        elif plot_lib == 'plotly':
            py = plotly_preamble + py
        else:
            py = pyplot_preamble + pyplot_exec_prefix + py

        plot_result = get_plot_result(py, data)
        it = 0

        while plot_result.error or not plot_result.result:
            # If there is an error in the returned plot result, try fixing it by calling fix_python_bug().
            # Do a maximum number of attempt equal to max_retries.
            if it == max_retries:
                raise Exception(f"Error: tried recovering {max_retries} times from Python fixing loop, now erroring\n" * 2)

            corrected = fix_python_bug(plot_result, it)
            print(corrected)
            corrected["type"] = "python-error"
            query_fixes.append(corrected)
            plot_result = get_plot_result(corrected["corrected"], data)
            it += 1

        if plot_result.result:
            break
    else:
        if plot_result.error:
            plot_result['result'] = f"Stumped me. Here's the code I came up with but it had the following error: {plot_result.error}."
        else:
            plot_result['result'] = f"Stumped me. Here's the code I came up with but it didn't return a result."

    return plot_result


def handle_plot_request(request: dict, tables_summary) -> dict:
    result = request["sql_result"]
    if result["error"]:
        request["plot_result"] = {}
        return request

    plot_lib = 'plotly'
    resp = chart_completion(request["question"], result["result"], plot_lib=plot_lib, tables_summary=tables_summary)
    responses = [resp]
    # NOTE: print statements make the streamlit application crash. Comment out for now.
    # TODO 2023-04-24: move from prints to proper logging.
    # print(f"INPUT DATA TO CHART PIPELINE: \n\n{result['result']}")
    # print("END OF DATA INPUT TO CHART PIPELINE")
    # TODO 2023-04-19: pass the result of the SQL query to data instead of sample of result. unless it shouldnt be that result['result'] is just a sample
    plot_result = plot_completion_pipeline(completions=responses, data=result["result"], plot_lib=plot_lib)
    resp = None
    if plot_result.result:
        pass
        # url = upload_image_s3(plot_result.result)
    request["plot_result"] = {"python": plot_result.python, "chart_url": "foo", "error": plot_result.error}
    return request


def plot_charts(sql_results: List, tables_summary):
    chart_results = []
    for request in sql_results:
        result = handle_plot_request(request, tables_summary)
        chart_results.append(result)
    return chart_results
