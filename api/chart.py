import io
import plotly.graph_objects as go
import json
from flask import make_response
from dataclasses import asdict

from api.chartgpt import ContextLengthError, QueryResult, answer_user_query


def generate_chart(body):
    question = body["question"]
    chart_type = body.get("type", "json")

    if chart_type == "json":
        try:
            query_result: QueryResult = answer_user_query(question)
        except ContextLengthError:
            return {"error": "Could not generate chart"}, 400
        if not query_result.chart:
            return {"error": "Could not generate chart"}, 400
        else:
            return asdict(query_result), 200
    elif chart_type == "png":
        try:
            query_result: QueryResult = answer_user_query(question)
        except ContextLengthError:
            return {"error": "Could not generate chart"}, 400
        if not query_result.chart:
            return {"error": "Could not generate chart"}, 400
        else:
            figure_json_string = query_result.chart
            figure_json = json.loads(figure_json_string, strict=False)
            fig = go.Figure(figure_json)

            img_byte_arr = io.BytesIO()
            fig.write_image(img_byte_arr, format="png")
            png_data = img_byte_arr.getvalue()

            response = make_response(png_data)
            response.headers.set("content-type", "image/png")
            return response, 200
