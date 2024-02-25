"""Module that acts as the entry point for the FastAPI application."""
from fastapi import FastAPI

# Local
from routes.lichess import router as lichess_router

app = FastAPI()
app.include_router(lichess_router, prefix="/lichess")


@app.get("/")
async def root():
    """Heartbeat/Ping check"""
    return {"ping": "pong"}
