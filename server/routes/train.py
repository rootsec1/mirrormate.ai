from fastapi import APIRouter

# Local
from scripts.util import get_cached_usernames, get_game_history_df, init_gemini_model, compute_next_move


router = APIRouter()
__cached_username_set__ = get_cached_usernames()

gemini_model = init_gemini_model()


@router.get("/persona/{lichess_username}")
async def train_persona(lichess_username: str):
    """Train the model for the given lichess_username"""
    return list(__cached_username_set__)


@router.get("/next-move/")
async def get_next_move(lichess_username: str, partial_sequence: str):
    """Return the next move in the game."""
    game_history_df = get_game_history_df(lichess_username)
    predicted_move = compute_next_move(
        partial_sequence,
        game_history_df,
        gemini_model
    )
    return predicted_move
