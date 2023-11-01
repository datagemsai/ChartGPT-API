# ResponseUsage

The usage of the request.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tokens** | **object** | The number of tokens used for the request. | [optional] 

## Example

```python
from chartgpt_client.models.response_usage import ResponseUsage

# TODO update the JSON string below
json = "{}"
# create an instance of ResponseUsage from a JSON string
response_usage_instance = ResponseUsage.from_json(json)
# print the JSON string representation of the object
print ResponseUsage.to_json()

# convert the object into a dict
response_usage_dict = response_usage_instance.to_dict()
# create an instance of ResponseUsage from a dict
response_usage_form_dict = response_usage.from_dict(response_usage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


