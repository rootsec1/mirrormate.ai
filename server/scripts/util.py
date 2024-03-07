import csv
import os
import berserk
import torch

from tqdm import tqdm
from transformers import T5Tokenizer, T5ForConditionalGeneration

LICHESS_API_TOKEN = os.environ["LICHESS_API_TOKEN"]
berserk_session = berserk.TokenSession(LICHESS_API_TOKEN)
berserk_client = berserk.Client(session=berserk_session)


__MODEL_DIR__ = "models/t5"
# Load the trained model and tokenizer
t5_small_model = T5ForConditionalGeneration.from_pretrained(__MODEL_DIR__)
t5_small_tokenizer = T5Tokenizer.from_pretrained(__MODEL_DIR__)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


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
    csv_list = os.listdir("data/processed")
    csv_list = [csv_file for csv_file in csv_list if csv_file.endswith(".csv")]
    cached_username_set = set()
    for csv_file in csv_list:
        username = csv_file.replace("sequence_target_map_", "")
        username = username.replace(".csv", "")
        cached_username_set.add(username)
    return cached_username_set


def preprocess_lichess_export_data(lichess_username: str) -> list[dict]:
    data_file_name = f"data/raw/games_{lichess_username}.csv"
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


def predict_next_move_using_t5_model(sequence) -> str:
    t5_small_model.to(device)

    # Prepare the text input for T5 format
    input_text = f"chess moves: {sequence}"
    input_ids = t5_small_tokenizer.encode(
        input_text,
        return_tensors="pt"
    ).to(device)

    # Generate the output
    output_ids = t5_small_model.generate(
        input_ids,
        max_length=16,
        num_beams=8,
        early_stopping=True
    )
    output = t5_small_tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return output
