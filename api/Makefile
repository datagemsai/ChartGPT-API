.DEFAULT_GOAL := generate_clients

generate_clients:
	generate_python_client

generate_python_client:
	openapi-generator generate -i api/openapi/openapi.yaml -g python -o ./api/clients/python_client/

install_clients:
	install_python_client

install_python_client:
	pip install ./api/clients/python_client/
