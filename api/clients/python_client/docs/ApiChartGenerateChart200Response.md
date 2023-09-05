# ApiChartGenerateChart200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The description of the analysis. | [optional] 
**query** | **str** | The generated SQL query. | [optional] 
**code** | **str** | The generated Python code. | [optional] 
**chart** | **str** | The generated Plotly chart JSON string. | [optional] 
**output** | **str** | The stdout output of the Python code. | [optional] 
**dataframe** | **str** | The generated Pandas dataframe. | [optional] 

## Example

```python
from chartgpt_client.models.api_chart_generate_chart200_response import ApiChartGenerateChart200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ApiChartGenerateChart200Response from a JSON string
api_chart_generate_chart200_response_instance = ApiChartGenerateChart200Response.from_json(json)
# print the JSON string representation of the object
print ApiChartGenerateChart200Response.to_json()

# convert the object into a dict
api_chart_generate_chart200_response_dict = api_chart_generate_chart200_response_instance.to_dict()
# create an instance of ApiChartGenerateChart200Response from a dict
api_chart_generate_chart200_response_form_dict = api_chart_generate_chart200_response.from_dict(api_chart_generate_chart200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


