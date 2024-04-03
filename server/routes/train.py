from fastapi import APIRouter

# Local
from scripts.util import *
from chess_client import ChessClient

router = APIRouter()


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
    game_history_df.to_csv(f"../data/raw/games_{lichess_username}.csv")

    exploded_game_list = []
    for game in game_history_list:
        exploded_game_list.extend(
            explode_game_into_moves(game, lichess_username)
        )

    # Convert explode_game_into_moves to a DataFrame
    exploded_game_df = pd.DataFrame(
        exploded_game_list,
        columns=["game_id", "input_sequence", "target_move"]
    )
    exploded_game_df.to_csv(
        f"../data/processed/sequence_target_map_{lichess_username}.csv",
        index="game_id"
    )

    return {"status": "CLONING_COMPLETE"}


@router.get("/next-move/")
async def get_next_move(lichess_username: str, partial_sequence: str):
    """Return the next move in the game."""
    game_history_df = get_game_history_df(lichess_username)
    chess_client = ChessClient(
        move_list_in_san=partial_sequence.strip().split(" "),
        lichess_username=lichess_username
    )
    predicted_move = chess_client.compute_next_move(game_history_df)
    return predicted_move
