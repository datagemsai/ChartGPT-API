# ApiRequestAskChartgptRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt** | **str** | The prompt based on which the response will be generated. | [optional] 
**dataset_id** | **str** | The dataset ID based on which the response will be generated. | [optional] [default to '']
**output_type** | [**OutputType**](OutputType.md) |  | [optional] 
**max_outputs** | **int** | The maximum number of outputs to generate. | [optional] [default to 10]
**max_attempts** | **int** | The maximum number of attempts to generate an output. | [optional] [default to 10]
**max_tokens** | **int** | The maximum number of tokens to use for generating an output. | [optional] [default to 10]
**stream** | **bool** | Whether to stream the response. | [optional] [default to False]

## Example

```python
from chartgpt_client.models.api_request_ask_chartgpt_request import ApiRequestAskChartgptRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApiRequestAskChartgptRequest from a JSON string
api_request_ask_chartgpt_request_instance = ApiRequestAskChartgptRequest.from_json(json)
# print the JSON string representation of the object
print ApiRequestAskChartgptRequest.to_json()

# convert the object into a dict
api_request_ask_chartgpt_request_dict = api_request_ask_chartgpt_request_instance.to_dict()
# create an instance of ApiRequestAskChartgptRequest from a dict
api_request_ask_chartgpt_request_form_dict = api_request_ask_chartgpt_request.from_dict(api_request_ask_chartgpt_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


