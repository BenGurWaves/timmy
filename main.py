"""
main.py

This is the entry point for the Timmy AI agent application.
It starts the FastAPI web server, which in turn initializes the Agent.
"""

import uvicorn
from config import WEB_SERVER_HOST, WEB_SERVER_PORT

if __name__ == "__main__":
    print(f"Starting Timmy AI web server on http://{WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
    print(f"Open http://localhost:{WEB_SERVER_PORT} in your browser to chat with Timmy.")
    uvicorn.run("server:app", host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, reload=False)
