from api.run import app
import logging


# Run the app
app.run(port=8081, debug=True)
app.logger.setLevel(logging.DEBUG)
