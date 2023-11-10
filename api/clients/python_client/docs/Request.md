# Request

Request

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data_source_url** | **object** | The data source URL based on which the response will be generated. The entity is optional. If not specified, the default data source will be used. | [optional] 
**session_id** | **object** | The job ID of the request. | [optional] 
**max_attempts** | **object** | The maximum number of attempts to generate an output. | [optional] 
**max_outputs** | **object** | The maximum number of outputs to generate. | [optional] 
**max_tokens** | **object** | The maximum number of tokens to use for generating an output. | [optional] 
**messages** | **object** | The messages based on which the response will be generated. | [optional] 
**output_type** | [**OutputType**](OutputType.md) |  | [optional] 

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


