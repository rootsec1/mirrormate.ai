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


# Local
LICHESS_API_TOKEN = os.environ["LICHESS_API_TOKEN"]
berserk_session = berserk.TokenSession(LICHESS_API_TOKEN)
berserk_client = berserk.Client(session=berserk_session)


def get_game_history_df(lichess_username: str) -> pd.DataFrame:
    game_history_file_path = f"../data/processed/sequence_target_map_{lichess_username}.csv"
    game_history_df = pd.read_csv(game_history_file_path, index_col=None)
    game_history_df = game_history_df.dropna()
    return game_history_df


def get_games_and_moves_by_username(username: str) -> list[dict]:
    """Get the games and moves of a user by their username."""
    games = berserk_client.games.export_by_player(
        username,
        analysed=False,
        evals=False,
        moves=True
    )
    game_list = []
    for game in tqdm(games):
        variant = game.get("variant", None)
        if variant != "standard":
            continue
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


def get_cached_usernames() -> set[str]:
    csv_list = os.listdir("../data/raw")
    csv_list = [csv_file for csv_file in csv_list if csv_file.endswith(".csv")]
    cached_username_set = set()
    for csv_file in csv_list:
        username = csv_file.replace("games_", "")
        username = username.replace(".csv", "")
        cached_username_set.add(username)
    return cached_username_set


def preprocess_lichess_export_data(lichess_username: str) -> list[dict]:
    data_file_name = f"../data/raw/games_{lichess_username}.csv"
    game_list: list = []

    with open(data_file_name, "r") as data_file:
        csv_reader = csv.DictReader(data_file)
        for row in csv_reader:
            game_list.append(row)

    return game_list


def explode_game_into_moves(game: dict, lichess_username: str) -> list[dict]:
    encoded_moves = []

    game_id = game.get("game_id")
    white_player = game.get("white_player")

    move_list = game.get("move_list")
    move_list = move_list.split(" ")
    move_list_length = len(move_list)

    generator_start_index = 0 if white_player == lichess_username else 1

    for i in range(generator_start_index, move_list_length, 2):
        if i == 0:
            input_sequence = None
        else:
            input_sequence = " ".join(move_list[:i])
        # The target move is the next move in the sequence
        target_move = move_list[i]
        encoded_moves.append((game_id, input_sequence, target_move))

    return encoded_moves


def make_prediction_using_model(moves_in_san_str: str, lichess_username: str) -> str:
    model_config_path = f"../models/{lichess_username}/model_arch.json"
    model_weights_path = f"../models/{lichess_username}/model_weights.h5"
    tokenizer_path = f"../models/{lichess_username}/tokenizer.pickle"
    label_encoder_path = f"../models/{lichess_username}/label_encoder.pickle"

    with open(model_config_path, "r") as model_config_file:
        model_config = model_config_file.read()
    model = model_from_json(model_config)
    model.load_weights(model_weights_path)

    with open(tokenizer_path, "rb") as tokenizer_file:
        tokenizer = pickle.load(tokenizer_file)

    with open(label_encoder_path, "rb") as label_encoder_file:
        label_encoder = pickle.load(label_encoder_file)

    model.compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"]
    )

    moves_in_san_str = moves_in_san_str.strip()
    sequence = tokenizer.texts_to_sequences([moves_in_san_str])
    padded_sequence = pad_sequences(
        sequence,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="pre"
    )
    prediction = model.predict(padded_sequence)
    predicted_move_index = np.argmax(prediction)
    predicted_move = label_encoder.inverse_transform([predicted_move_index])
    return str(predicted_move[0]).strip()
