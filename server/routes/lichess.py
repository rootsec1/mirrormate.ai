"""Routes for interactions with lichess API."""

# Import the APIRouter from FastAPI to create API routes
from fastapi import APIRouter

# Import the get_games_and_moves_by_username function from the local scripts.util module
from scripts.util import get_games_and_moves_by_username

# Create a new API router
router = APIRouter()


@router.get("/history/{username}")
async def get_history(username: str):
    """
    Return the game history of the user.

    Args:
        username (str): The username of the user.

    Returns:
        list[dict]: A list of dictionaries, each representing a game.
    """
    # Call the get_games_and_moves_by_username function to get the games and moves of the user
    games = get_games_and_moves_by_username(username)
    # Return the games and moves
    return games
