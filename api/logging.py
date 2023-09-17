import logging
from api.run import app

logger = app.app.logger
logger.setLevel(logging.DEBUG)
