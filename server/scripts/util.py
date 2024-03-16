import io
import csv
import os
import berserk
import pandas as pd
import google.generativeai as genai
import chess
import chess.svg
import ollama
import json

from PIL import Image
from tqdm import tqdm
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from stockfish import Stockfish


from constants import LLM_NEXT_MOVE_PROMPT

LICHESS_API_TOKEN = os.environ["LICHESS_API_TOKEN"]
berserk_session = berserk.TokenSession(LICHESS_API_TOKEN)
berserk_client = berserk.Client(session=berserk_session)

stockfish = Stockfish("/opt/homebrew/bin/stockfish")


def get_game_history_df(lichess_username: str) -> pd.DataFrame:
    game_history_file_path = f"data/processed/sequence_target_map_{lichess_username}.csv"
    game_history_df = pd.read_csv(game_history_file_path, index_col=None)
    game_history_df = game_history_df.dropna()
    return game_history_df


def init_gemini_model() -> genai.GenerativeModel:
    GOOGLE_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        "models/gemini-pro",
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )
    return model


def san_to_uci(san_moves):
    # If no board is provided, create a new one
    board = chess.Board()
    uci_moves = []

    for san in san_moves:
        # Convert the SAN move to a move object
        move = board.parse_san(san)
        # Convert the move object to UCI format
        uci = move.uci()
        uci_moves.append(uci)
        # Make the move on the board
        board.push(move)

    return uci_moves


# Function to evaluate a sequence of moves using Stockfish
def determine_stockfish_intelligence_level(moves):
    stockfish.set_position([])  # Reset the board to the initial position
    player_score = 0  # Initialize player score

    for move in moves:
        best_move = stockfish.get_best_move()
        if move == best_move:
            player_score += 1  # Increment score if the player's move matches Stockfish's best move
        stockfish.make_moves_from_current_position([move])

    # Calculate the intelligence level as a percentage
    intelligence_level = (player_score / len(moves)) * 100 if moves else 20
    return intelligence_level


def compute_next_move(
    partial_sequence: str,
    game_history_df: pd.DataFrame,
    model: genai.GenerativeModel
) -> str:
    partial_sequence_list = partial_sequence.split(" ")
    formatted_partial_sequence = (" ".join(partial_sequence_list)).strip()

    board = chess.Board()
    for move in partial_sequence_list:
        board.push_san(move)

    subset_df = game_history_df[
        game_history_df["input_sequence"] == formatted_partial_sequence
    ]
    if not subset_df.empty:
        target_move = subset_df["target_move"].value_counts().idxmax()
        return {
            "predicted_move": target_move,
            "source": "cache"
        }

    formatted_move_list = ""
    for move in partial_sequence_list:
        subset_df = game_history_df[
            game_history_df["input_sequence"].str.startswith(move)
        ]
        # Keep only the last row from that game_id in subset_df even if not a duplicate
        subset_df = subset_df.drop_duplicates(subset=["game_id"], keep="last")
        subset_df = subset_df[["input_sequence", "target_move"]]
        subset_df = subset_df.drop_duplicates()
        input_sequence_str = subset_df["input_sequence"].tolist()

        input_sequence_str = "\n".join(input_sequence_str)
        formatted_move_list += input_sequence_str

    # Get legal moves
    legal_move_list = board.legal_moves
    legal_move_list = set([board.san(move) for move in legal_move_list])

    # Get the next move from the model
    prompt = LLM_NEXT_MOVE_PROMPT.format(
        formatted_move_list=formatted_move_list,
        formatted_legal_move_list="\n".join(legal_move_list),
        formatted_partial_sequence=formatted_partial_sequence
    )

    try:
        response = model.generate_content(prompt)
        response = str(response.text).strip()
        # response = ollama.generate(
        #     prompt=prompt,
        #     model="gemma:2b",
        # )
        # response = str(response.get("response")).strip()

        response = json.loads(response)
        response = response["move"]
        if response not in legal_move_list:
            response = list(legal_move_list)[0]

        return {
            "predicted_move": response,
            "source": "model"
        }
    except Exception as ex:
        # Get stockfish intelligence level from partial_sequence which is a list of SAN moves
        uci_moves = san_to_uci(partial_sequence_list)
        intelligence_level = determine_stockfish_intelligence_level(
            uci_moves
        )
        stockfish.set_position(partial_sequence_list)
        stockfish.set_skill_level(intelligence_level)
        # Get the best move from Stockfish
        best_move = stockfish.get_best_move()

        return {
            "predicted_move": best_move,
            "source": "stockfish"
        }


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
    csv_list = os.listdir("data/raw")
    csv_list = [csv_file for csv_file in csv_list if csv_file.endswith(".csv")]
    cached_username_set = set()
    for csv_file in csv_list:
        username = csv_file.replace("games_", "")
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
