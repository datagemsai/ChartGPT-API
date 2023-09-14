# Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the request. | [optional] 
**created_at** | **int** | The timestamp of when the request was created. | [optional] 
**finished_at** | **int** | The timestamp of when the request was finished. | [optional] 
**status** | [**Status**](Status.md) |  | [optional] 
**messages** | [**List[ResponseMessagesInner]**](ResponseMessagesInner.md) | The messages of the request. | [optional] 
**dataset_id** | **str** | The dataset ID of the request. | [optional] 
**attempts** | [**List[Attempt]**](Attempt.md) | The attempts of the request. | [optional] 
**output_type** | [**OutputType**](OutputType.md) |  | [optional] 
**outputs** | [**List[Output]**](Output.md) | The outputs of the request. | [optional] 
**errors** | [**List[Error]**](Error.md) | The errors of the request. | [optional] 
**usage** | [**ResponseUsage**](ResponseUsage.md) |  | [optional] 

## Example

```python
from chartgpt_client.models.response import Response

# TODO update the JSON string below
json = "{}"
# create an instance of Response from a JSON string
response_instance = Response.from_json(json)
# print the JSON string representation of the object
print Response.to_json()

# convert the object into a dict
response_dict = response_instance.to_dict()
# create an instance of Response from a dict
response_form_dict = response.from_dict(response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


