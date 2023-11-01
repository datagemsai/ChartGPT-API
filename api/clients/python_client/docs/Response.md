# Response

Response

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attempts** | **object** | The attempts of the request. | [optional] 
**created_at** | **object** | The timestamp of when the request was created. | [optional] 
**data_source_url** | **object** | The data source URL of the request. | [optional] 
**errors** | **object** | The errors of the request. | [optional] 
**finished_at** | **object** | The timestamp of when the request was finished. | [optional] 
**job_id** | **object** | The job ID of the response. | [optional] 
**messages** | **object** | The messages of the request. | [optional] 
**output_type** | [**OutputType**](OutputType.md) |  | [optional] 
**outputs** | **object** | The outputs of the request. | [optional] 
**status** | [**Status**](Status.md) |  | [optional] 
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


