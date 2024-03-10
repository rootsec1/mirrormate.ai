"""Module that acts as the entry point for the FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local
from routes.lichess import router as lichess_router
from routes.train import router as train_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


app.include_router(lichess_router, prefix="/lichess")
app.include_router(train_router, prefix="/train")


@app.get("/")
async def root():
    """Heartbeat/Ping check"""
    return {"ping": "pong"}
