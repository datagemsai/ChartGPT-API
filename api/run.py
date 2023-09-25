import logging
from logging.config import dictConfig

import connexion

dictConfig(
    {
        "version": 1,
        "filters": {
            "job_id": {
                "()": "api.logging.JobIdFilter",
            },
        },
        "formatters": {
            "default": {
                "format": "[%(asctime)s job_id:%(job_id)s %(module)s->%(funcName)s():%(lineno)s] %(levelname)s: %(message)s"
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
                "filters": ["job_id"],
            },
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
        "loggers": {
            "chartgpt": {"level": "DEBUG"},
        },
    }
)

# Create a new Connexion app instance
app = connexion.App(__name__, specification_dir="openapi/")

# Read the swagger.yaml file to configure the endpoints
app.add_api("openapi_v1.yaml")
