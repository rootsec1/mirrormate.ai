"""Module that acts as the entry point for the FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers from local modules
from routes.lichess import router as lichess_router
from routes.train import router as train_router

# Initialize the FastAPI application
app = FastAPI()

# Add CORS middleware to the application
# This allows requests from any origin, with any method, and any headers
# It also allows sending credentials with the requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Include the routers for the lichess and train endpoints
# The routers handle requests to their respective endpoints
app.include_router(lichess_router, prefix="/lichess")
app.include_router(train_router, prefix="/train")


@app.get("/")
async def root():
    """
    Heartbeat/Ping check.
    This endpoint is used to check if the server is running.
    It returns a simple JSON response {"ping": "pong"}.
    """
    return {"ping": "pong"}
