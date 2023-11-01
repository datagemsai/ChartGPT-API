import json
import requests
import yaml
from pathlib import Path


response = requests.get("http://localhost:8081/openapi.json")
response.raise_for_status()
openapi_content = response.json()

for path_data in openapi_content["paths"].values():
    for operation in path_data.values():
        print(operation)
        tag = operation["tags"][0]
        operation_id = operation["operationId"]
        to_remove = f"{tag}-"
        new_operation_id = operation_id[len(to_remove) :]
        operation["operationId"] = new_operation_id

file_path = Path(__file__).parent / "openapi_v1.yaml"
file_path.write_text(yaml.dump(openapi_content))
