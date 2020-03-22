from eNMS.framework import create_app
# --- begin ien-AP change - Mazzucco ---
from os import getenv
from werkzeug.serving import WSGIRequestHandler
# --- end ien-AP change - Mazzucco ---

app = create_app()

# --- begin ien-AP change - Mazzucco ---
if __name__ == '__main__':
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True,
            port=getenv("FLASK_APP_PORT", 5000))
# --- end ien-AP change - Mazzucco ---



