import connexion


def create_app():
    # Create a new Connexion app instance
    app = connexion.App(__name__, specification_dir='openapi/')
    
    # Read the swagger.yaml file to configure the endpoints
    app.add_api('openapi.yaml')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=8080)
