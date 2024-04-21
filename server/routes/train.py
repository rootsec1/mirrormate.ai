from fastapi import APIRouter

# Local
from scripts.util import *
from chess_client import ChessClient

# Create a new API router
router = APIRouter()


@router.get("/persona/{lichess_username}")
async def train_persona(lichess_username: str):
    """
    Train the persona of a user.

    Args:
        lichess_username (str): The Lichess username of the user.

    Returns:
        dict: A dictionary containing the status of the operation.
    """
    # Get the set of cached usernames
    cached_username_set = get_cached_usernames()
    # If the username is in the set, return a status indicating that the cloning is complete
    if lichess_username in cached_username_set:
        return {"status": "CLONING_COMPLETE"}

    # Get the games and moves of the user
    game_history_list = get_games_and_moves_by_username(lichess_username)
    # Convert the list to a DataFrame
    game_history_df = pd.DataFrame(game_history_list)
    # Replace any missing player names with "ANONYMOUS"
    game_history_df["white_player"] = game_history_df["white_player"].replace(
        "", "ANONYMOUS")
    game_history_df["black_player"] = game_history_df["black_player"].replace(
        "", "ANONYMOUS")
    game_history_df["winning_player"] = game_history_df["winning_player"].replace(
        "", "ANONYMOUS")
    # Save the DataFrame to a CSV file
    game_history_df.to_csv(f"../data/raw/games_{lichess_username}.csv")

    # Explode the games into moves
    exploded_game_list = []
    for game in game_history_list:
        exploded_game_list.extend(
            explode_game_into_moves(game, lichess_username))

    # Convert the list of exploded games to a DataFrame
    exploded_game_df = pd.DataFrame(exploded_game_list, columns=[
                                    "game_id", "input_sequence", "target_move"])
    # Save the DataFrame to a CSV file
    exploded_game_df.to_csv(
        f"../data/processed/sequence_target_map_{lichess_username}.csv", index="game_id")

    # Return a status indicating that the cloning is complete
    return {"status": "CLONING_COMPLETE"}


@router.get("/next-move/")
async def get_next_move(lichess_username: str, partial_sequence: str):
    """
    Get the next move in the game.

    Args:
        lichess_username (str): The Lichess username of the user.
        partial_sequence (str): The partial sequence of moves.

    Returns:
        str: The next move in the game.
    """
    # Get the game history of the user
    game_history_df = get_game_history_df(lichess_username)
    # Create a ChessClient object
    chess_client = ChessClient(move_list_in_san=partial_sequence.strip().split(
        " "), lichess_username=lichess_username)
    # Compute the next move using the ChessClient object
    predicted_move = chess_client.compute_next_move(game_history_df)
    # Return the predicted move
    return predicted_move
