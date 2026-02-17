"""
main.py

This is the entry point for the Timmy AI agent application.
It starts the FastAPI web server, which in turn initializes the Agent.
"""

import uvicorn
from server import app
from config import WEB_SERVER_HOST, WEB_SERVER_PORT

if __name__ == "__main__":
    print(f"Starting Timmy AI web server on http://{WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
    uvicorn.run(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
