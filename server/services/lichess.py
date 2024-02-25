"""Lichess API client."""

import berserk
import pandas as pd

from tqdm import tqdm

# Local
from constants import LICHESS_API_TOKEN

session = berserk.TokenSession(LICHESS_API_TOKEN)
client = berserk.Client(session=session)


def get_games_and_moves_by_username(username: str) -> list[dict]:
    """Get the games and moves of a user by their username."""
    games = client.games.export_by_player(
        username,
        analysed=False,
        evals=False,
        moves=True
    )
    game_list = []
    for game in tqdm(games):
        game_id = game.get("id", "")
        players = game.get("players", {})
        white_player = players.get("white", {}).get("user", {}).get("name", "")
        black_player = players.get("black", {}).get("user", {}).get("name", "")
        winning_player = game.get("winner", "")
        winning_player = white_player if winning_player == "white" else black_player
        move_list = game.get("moves", "")

        game_summary_dict = {
            "game_id": game_id,
            "white_player": white_player,
            "black_player": black_player,
            "winning_player": winning_player,
            "move_list": move_list,
        }
        game_list.append(game_summary_dict)
    return game_list
