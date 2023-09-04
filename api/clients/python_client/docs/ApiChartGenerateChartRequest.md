# ApiChartGenerateChartRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**question** | **str** | The question based on which the chart will be generated. | [optional] 
**type** | **str** | The format in which the chart should be returned. Accepted values are &#x60;json&#x60; or &#x60;png&#x60;. | [optional] [default to 'json']

## Example

```python
from openapi_client.models.api_chart_generate_chart_request import ApiChartGenerateChartRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApiChartGenerateChartRequest from a JSON string
api_chart_generate_chart_request_instance = ApiChartGenerateChartRequest.from_json(json)
# print the JSON string representation of the object
print ApiChartGenerateChartRequest.to_json()

# convert the object into a dict
api_chart_generate_chart_request_dict = api_chart_generate_chart_request_instance.to_dict()
# create an instance of ApiChartGenerateChartRequest from a dict
api_chart_generate_chart_request_form_dict = api_chart_generate_chart_request.from_dict(api_chart_generate_chart_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


