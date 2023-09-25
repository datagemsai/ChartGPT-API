import connexion
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s %(module)s->%(funcName)s():%(lineno)s] %(levelname)s: %(message)s'
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# Create a new Connexion app instance
app = connexion.App(__name__, specification_dir="openapi/")

# Read the swagger.yaml file to configure the endpoints
app.add_api("openapi_v1.yaml")
