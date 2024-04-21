import csv
import os
import pickle
import berserk
import numpy as np
import pandas as pd

from tqdm import tqdm
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import model_from_json

from constants import MAX_SEQUENCE_LENGTH

# Get the Lichess API token from the environment variables
LICHESS_API_TOKEN = os.environ["LICHESS_API_TOKEN"]
# Create a Berserk session and client using the Lichess API token
berserk_session = berserk.TokenSession(LICHESS_API_TOKEN)
berserk_client = berserk.Client(session=berserk_session)


def get_game_history_df(lichess_username: str) -> pd.DataFrame:
    """
    Get the game history DataFrame of a user by their Lichess username.

    Args:
        lichess_username (str): The Lichess username of the user.

    Returns:
        pd.DataFrame: The game history DataFrame of the user.
    """
    # Define the path of the game history file
    game_history_file_path = f"../data/processed/sequence_target_map_{lichess_username}.csv"
    # Read the game history file into a DataFrame
    game_history_df = pd.read_csv(game_history_file_path, index_col=None)
    # Drop any rows with missing values
    game_history_df = game_history_df.dropna()
    return game_history_df


def get_games_and_moves_by_username(username: str) -> list[dict]:
    """
    Get the games and moves of a user by their username.

    Args:
        username (str): The username of the user.

    Returns:
        list[dict]: A list of dictionaries, each representing a game.
    """
    # Export the games of the user using the Berserk client
    games = berserk_client.games.export_by_player(
        username,
        analysed=False,
        evals=False,
        moves=True
    )
    game_list = []
    # Loop through each game
    for game in tqdm(games):
        # Skip the game if its variant is not "standard"
        variant = game.get("variant", None)
        if variant != "standard":
            continue
        # Get the game ID, players, and moves
        game_id = game.get("id", "")
        players = game.get("players", {})
        white_player = players.get("white", {}).get("user", {}).get("name", "")
        black_player = players.get("black", {}).get("user", {}).get("name", "")
        winning_player = game.get("winner", "")
        winning_player = white_player if winning_player == "white" else black_player
        move_list = game.get("moves", "")

        # Create a dictionary summarizing the game
        game_summary_dict = {
            "game_id": game_id,
            "white_player": white_player,
            "black_player": black_player,
            "winning_player": winning_player,
            "move_list": move_list,
        }
        # Add the game summary dictionary to the list
        game_list.append(game_summary_dict)
    return game_list


def get_cached_usernames() -> set[str]:
    """
    Get the usernames of the users whose games are cached.

    Returns:
        set[str]: A set of usernames.
    """
    # Get the list of CSV files in the raw data directory
    csv_list = os.listdir("../data/raw")
    csv_list = [csv_file for csv_file in csv_list if csv_file.endswith(".csv")]
    cached_username_set = set()
    # Loop through each CSV file
    for csv_file in csv_list:
        # Extract the username from the file name
        username = csv_file.replace("games_", "")
        username = username.replace(".csv", "")
        # Add the username to the set
        cached_username_set.add(username)
    return cached_username_set


def preprocess_lichess_export_data(lichess_username: str) -> list[dict]:
    """
    Preprocess the Lichess export data of a user.

    Args:
        lichess_username (str): The Lichess username of the user.

    Returns:
        list[dict]: A list of dictionaries, each representing a game.
    """
    # Define the path of the data file
    data_file_name = f"../data/raw/games_{lichess_username}.csv"
    game_list: list = []

    # Open the data file
    with open(data_file_name, "r") as data_file:
        csv_reader = csv.DictReader(data_file)
        # Loop through each row in the CSV file
        for row in csv_reader:
            # Add the row to the list
            game_list.append(row)

    return game_list


def explode_game_into_moves(game: dict, lichess_username: str) -> list[dict]:
    """
    Explode a game into moves.

    Args:
        game (dict): A dictionary representing a game.
        lichess_username (str): The Lichess username of the user.

    Returns:
        list[dict]: A list of dictionaries, each representing a move.
    """
    encoded_moves = []

    # Get the game ID, white player, and move list
    game_id = game.get("game_id")
    white_player = game.get("white_player")
    move_list = game.get("move_list")
    move_list = move_list.split(" ")
    move_list_length = len(move_list)

    # Determine the start index of the generator based on the white player
    generator_start_index = 0 if white_player == lichess_username else 1

    # Loop through each move in the move list
    for i in range(generator_start_index, move_list_length, 2):
        if i == 0:
            input_sequence = None
        else:
            # Get the input sequence up to the current move
            input_sequence = " ".join(move_list[:i])
        # The target move is the next move in the sequence
        target_move = move_list[i]
        # Add the encoded move to the list
        encoded_moves.append((game_id, input_sequence, target_move))

    return encoded_moves


def make_prediction_using_model(moves_in_san_str: str, lichess_username: str) -> str:
    """
    Make a prediction using the model of a user.

    Args:
        moves_in_san_str (str): The moves in Standard Algebraic Notation (SAN) string.
        lichess_username (str): The Lichess username of the user.

    Returns:
        str: The predicted move.
    """
    # Define the paths of the model config, weights, tokenizer, and label encoder
    model_config_path = f"../models/{lichess_username}/model_arch.json"
    model_weights_path = f"../models/{lichess_username}/model_weights.h5"
    tokenizer_path = f"../models/{lichess_username}/tokenizer.pickle"
    label_encoder_path = f"../models/{lichess_username}/label_encoder.pickle"

    # Load the model config and weights
    with open(model_config_path, "r") as model_config_file:
        model_config = model_config_file.read()
    model = model_from_json(model_config)
    model.load_weights(model_weights_path)

    # Load the tokenizer and label encoder
    with open(tokenizer_path, "rb") as tokenizer_file:
        tokenizer = pickle.load(tokenizer_file)
    with open(label_encoder_path, "rb") as label_encoder_file:
        label_encoder = pickle.load(label_encoder_file)

    # Compile the model
    model.compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"]
    )

    # Preprocess the moves
    moves_in_san_str = moves_in_san_str.strip()
    sequence = tokenizer.texts_to_sequences([moves_in_san_str])
    padded_sequence = pad_sequences(
        sequence,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="pre"
    )
    # Make a prediction using the model
    prediction = model.predict(padded_sequence)
    predicted_move_index = np.argmax(prediction)
    predicted_move = label_encoder.inverse_transform([predicted_move_index])
    return str(predicted_move[0]).strip()
