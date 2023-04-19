

from typing import List
from .base import table_info, completion, double_check_query, fix_sql_bug, get_sql_result, sql_completion_pipeline, plot_completion_pipeline, pyplot_preamble, plotly_preamble
import pandas as pd


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
        prompt = f""" {tables_summary}\n
                As a world class expert software engineer and data scientist, given the above dataset, write a
                detailed and correct plotly code to produce a chart as requested:\n
                "{question}"
                \nUse st.plotly_chart(fig, use_container_width=True) to display the plot at the end. Do not forget to filter by dates if requested.
                Add axes names, units, legend. Update the layout accordingly for color-coded visualizations. 
                Keep code as succinct as possible and do not add comments.
```
""" + plotly_preamble
                # including colors
                # When requested for distributions, you should group by the object.
                # Comment the code with your logic.
                # When requested for distributions you should group by the object and not plot across time (where time column can be date, day, dt, block_time [...]).

    else:
        prompt = f"""records_df = pd.DataFrame.from_records({result})
    
    
        As a senior analyst, given the above data set, write detailed and correct matplotlib code to produce a chart as requested:
    
        "{question}"
    
        Comment the code with your logic. Use plt.show() to display the plot at the end.
    
        ```
        """ + pyplot_preamble
    print(prompt)
    resp = completion(prompt)
    return resp


def handle_plot_request(request: dict, tables_summary) -> dict:
    result = request["sql_result"]
    if result["error"]:
        request["plot_result"] = {}
        return request

    plot_lib = 'plotly'
    resp = chart_completion(request["question"], result["result"], plot_lib=plot_lib, tables_summary=tables_summary)
    responses = [resp]
    print(f"INPUT DATA TO CHART PIPELINE: \n\n{result['result']}")
    print("END OF DATA INPUT TO CHART PIPELINE")
    # TODO 2023-04-19: pass the result of the SQL query to data instead of sample of result. unless it shouldnt be that result['result'] is just a sample
    pr = plot_completion_pipeline(completions=responses, data=result["result"], plot_lib=plot_lib)
    resp = None
    if pr.result:
        pass
        # url = upload_image_s3(pr.result)
    request["plot_result"] = {"python": pr.python, "chart_url": "foo", "error": pr.error}
    return request


def plot_charts(sql_results: List, tables_summary):
    chart_results = []
    for request in sql_results:
        result = handle_plot_request(request, tables_summary)
        chart_results.append(result)
    return chart_results


