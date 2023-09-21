# Request


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**messages** | [**List[RequestMessagesInner]**](RequestMessagesInner.md) | The messages based on which the response will be generated. | [optional] 
**data_source_url** | **str** | The data source URL based on which the response will be generated. The entity is optional. If not specified, the default data source will be used. | [optional] [default to '']
**output_type** | [**OutputType**](OutputType.md) |  | [optional] 
**max_outputs** | **int** | The maximum number of outputs to generate. | [optional] [default to 10]
**max_attempts** | **int** | The maximum number of attempts to generate an output. | [optional] [default to 10]
**max_tokens** | **int** | The maximum number of tokens to use for generating an output. | [optional] [default to 10]

## Example

```python
from chartgpt_client.models.request import Request

# TODO update the JSON string below
json = "{}"
# create an instance of Request from a JSON string
request_instance = Request.from_json(json)
# print the JSON string representation of the object
print Request.to_json()

# convert the object into a dict
request_dict = request_instance.to_dict()
# create an instance of Request from a dict
request_form_dict = request.from_dict(request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


