from api.chartgpt import extract_code_generation_response_data

# JSONDecodeError: Expecting ',' delimiter
invalid_function_call_response = {
    "choices": [
        {
            "finish_reason": "stop", 
            "index": 0, 
            "message": {
                "function_call": {
                    "arguments": '{\n"docstring": "This function will calculate the average sale duration for properties that have had more than 10 viewings. It will also group the results by the number of bedrooms and furnishing status to see if these factors affect the average sale duration.",\n"code": \n"""\nimport pandas as pd\n\ndef answer_question(df: pd.DataFrame) -> pd.DataFrame:\n    avg_sale_duration = df.groupby([\'bed\', \'furnished\'])[\'avg_sale_duration\'].mean().reset_index()\n    return avg_sale_duration\n"""\n}',
                    "name": "execute_python_code"
                }, 
            }
        }
    ]
}

def test_extract_code_generation_response_data():
    _, _, _ = extract_code_generation_response_data(invalid_function_call_response)
