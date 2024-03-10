from fastapi import APIRouter

# Local
from scripts.util import *

router = APIRouter()
gemini_model = init_gemini_model()


@router.get("/persona/{lichess_username}")
async def train_persona(lichess_username: str):
    game_history_list = get_games_and_moves_by_username(lichess_username)
    game_history_df = pd.DataFrame(game_history_list)
    game_history_df["white_player"] = game_history_df["white_player"].replace(
        "",
        "ANONYMOUS"
    )
    game_history_df["black_player"] = game_history_df["black_player"].replace(
        "",
        "ANONYMOUS"
    )
    game_history_df["winning_player"] = game_history_df["winning_player"].replace(
        "",
        "ANONYMOUS"
    )
    game_history_df.to_csv(f"data/raw/games_{lichess_username}.csv")
    return {"status": "CLONING_COMPLETE"}


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
