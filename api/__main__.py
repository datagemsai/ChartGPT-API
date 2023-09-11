import connexion

# Create a new Connexion app instance
app = connexion.App(__name__, specification_dir="openapi/")

# Read the swagger.yaml file to configure the endpoints
app.add_api("openapi_v1.yaml")

# Run the app
app.run(port=8081)
