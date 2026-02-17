"""
server.py

FastAPI web server for Timmy AI chat interface.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import os

from agent import Agent
from config import WEB_SERVER_HOST, WEB_SERVER_PORT, PROJECT_ROOT

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_ROOT, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "templates"))

agent = Agent()


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/history")
async def get_history():
    """Returns chat history for restoring on page refresh."""
    try:
        history = agent.get_chat_history_for_display(50)
        return JSONResponse(content={"messages": history})
    except Exception as e:
        return JSONResponse(content={"messages": [], "error": str(e)})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            user_message = message.get("message")

            if user_message:
                try:
                    response_generator = agent.handle_message(user_message)
                    for response_chunk in response_generator:
                        await websocket.send_json(response_chunk)
                except Exception as e:
                    print(f"Agent error: {e}")
                    await websocket.send_json({"type": "error", "text": str(e)})

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "text": str(e)})
        except Exception:
            pass


if __name__ == "__main__":
    uvicorn.run(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
