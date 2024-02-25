"""Routes for interactions with lichess API."""

from fastapi import APIRouter

# Local
from services.lichess import get_games_and_moves_by_username

router = APIRouter()


@router.get("/history/{username}")
async def get_history(username: str):
    """Return the game history of the user."""
    games = get_games_and_moves_by_username(username)
    return games
