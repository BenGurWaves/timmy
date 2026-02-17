"""
server.py

This module implements the FastAPI web server for the Timmy AI agent's chat interface.
It handles API endpoints for chat, tool execution, and serves the static frontend files.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import os

from agent import Agent # Assuming Agent class is accessible
from config import WEB_SERVER_HOST, WEB_SERVER_PORT, PROJECT_ROOT

app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_ROOT, "static")), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "templates"))

# Initialize the agent (this will be done once when the server starts)
agent = Agent()

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    """
    Serves the main chat interface HTML page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections for real-time chat and agent interaction.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            user_message = message.get("message")

            if user_message:
                # Send a 'thinking' status to the frontend
                await websocket.send_json({"type": "status", "text": "Timmy is thinking..."})

                # Process the message with the agent
                response_generator = agent.handle_message(user_message)
                
                # Stream responses back to the client
                for response_chunk in response_generator:
                    await websocket.send_json(response_chunk)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({"type": "error", "text": str(e)})


if __name__ == "__main__":
    uvicorn.run(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
