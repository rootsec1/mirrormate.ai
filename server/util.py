import csv
import os


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
        encoded_moves.append((input_sequence, target_move))

    return encoded_moves
