# Attempt

Attempt

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **object** | The timestamp of when the attempt was created. | [optional] 
**errors** | **object** | The errors of the attempt. | [optional] 
**index** | **object** | The index of the attempt. | [optional] 
**outputs** | **object** | The outputs of the attempt. | [optional] 

## Example

```python
from chartgpt_client.models.attempt import Attempt

# TODO update the JSON string below
json = "{}"
# create an instance of Attempt from a JSON string
attempt_instance = Attempt.from_json(json)
# print the JSON string representation of the object
print Attempt.to_json()

# convert the object into a dict
attempt_dict = attempt_instance.to_dict()
# create an instance of Attempt from a dict
attempt_form_dict = attempt.from_dict(attempt_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


