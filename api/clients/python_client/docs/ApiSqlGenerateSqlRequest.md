# ApiSqlGenerateSqlRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**question** | **str** | The question based on which the SQL query will be generated. | [optional] 

## Example

```python
from openapi_client.models.api_sql_generate_sql_request import ApiSqlGenerateSqlRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApiSqlGenerateSqlRequest from a JSON string
api_sql_generate_sql_request_instance = ApiSqlGenerateSqlRequest.from_json(json)
# print the JSON string representation of the object
print ApiSqlGenerateSqlRequest.to_json()

# convert the object into a dict
api_sql_generate_sql_request_dict = api_sql_generate_sql_request_instance.to_dict()
# create an instance of ApiSqlGenerateSqlRequest from a dict
api_sql_generate_sql_request_form_dict = api_sql_generate_sql_request.from_dict(api_sql_generate_sql_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


