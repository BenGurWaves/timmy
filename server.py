"""
server.py

FastAPI web server for Timmy AI chat interface.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import os
import asyncio
import random
import time

from agent import Agent
from config import WEB_SERVER_HOST, WEB_SERVER_PORT, PROJECT_ROOT

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_ROOT, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "templates"))

agent = Agent()

# Start the subconscious loop
agent.subconscious.start()

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
    
    # Background task for UI updates (vibe, pulse, dreams, etc.)
    async def ui_updates():
        last_journal_count = len(agent.subconscious.journal)
        try:
            while True:
                # Send real-time updates for the new UI
                await websocket.send_json({"type": "vibe", "text": agent.subconscious.vibe})
                
                # Simulate pulse for now (real sensors would need a library)
                await websocket.send_json({"type": "pulse", "temp": random.randint(40, 55)})
                
                # Check for new journal entries
                current_journal_count = len(agent.subconscious.journal)
                if current_journal_count > last_journal_count:
                    new_entries = agent.subconscious.journal[last_journal_count:]
                    for entry in new_entries:
                        await websocket.send_json({
                            "type": "subconscious_thought", 
                            "text": f"[{entry['timestamp']}] {entry['content']}"
                        })
                    last_journal_count = current_journal_count
                
                await asyncio.sleep(2)
        except Exception as e:
            print(f"UI Update Task Error: {e}")
            pass

    update_task = asyncio.create_task(ui_updates())

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            user_message = message.get("message")

            if user_message:
                try:
                    # Run the generator in a thread to avoid blocking the event loop
                    # but since it's a generator yielding chunks, we iterate it here.
                    for response_chunk in agent.handle_message(user_message):
                        await websocket.send_json(response_chunk)
                except Exception as e:
                    print(f"Agent error: {e}")
                    await websocket.send_json({"type": "error", "text": str(e)})

    except WebSocketDisconnect:
        print("Client disconnected")
        update_task.cancel()
    except Exception as e:
        print(f"WebSocket error: {e}")
        update_task.cancel()
        try:
            await websocket.send_json({"type": "error", "text": str(e)})
        except Exception:
            pass


if __name__ == "__main__":
    uvicorn.run(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
