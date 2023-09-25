import os

from api.run import app

# Run the app
app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))
