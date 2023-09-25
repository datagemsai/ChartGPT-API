import os

import uvicorn

from api.run import app

# Run the app
uvicorn.run(
    app, host="0.0.0.0", port=int(os.environ.get("PORT", 8081)), log_level="debug"
)
