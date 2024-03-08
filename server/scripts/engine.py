import os
import sys
import pandas as pd
import google.generativeai as genai
import chess
import ollama
import json
import time

from google.generativeai.types import HarmCategory, HarmBlockThreshold


def get_game_history_df(lichess_username: str) -> pd.DataFrame:
    game_history_file_path = f"data/raw/games_{lichess_username}.csv"
    game_history_df = pd.read_csv(game_history_file_path)
    game_history_df = game_history_df.dropna()
    return game_history_df


def init_gemini_model() -> genai.GenerativeModel:
    GOOGLE_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        "gemini-pro",
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )
    return model


def compute_next_move(
    partial_sequence: str,
    game_history_df: pd.DataFrame,
    model: genai.GenerativeModel
) -> str:
    partial_sequence_list = partial_sequence.split(",")
    formatted_partial_sequence = (" ".join(partial_sequence_list)).strip()

    board = chess.Board()
    for move in partial_sequence_list:
        board.push_san(move)
    print(board)

    subset_df = game_history_df[
        game_history_df["move_list"]
        .str.startswith(formatted_partial_sequence)
    ]
    filtered_move_list = subset_df["move_list"].tolist()

    formatted_move_list = ""
    for idx, move_list_str in enumerate(filtered_move_list):
        formatted_move_list += f"Game {idx+1} = {move_list_str}\n"

    legal_move_list = board.legal_moves
    legal_move_list = set([board.san(move) for move in legal_move_list])
    formatted_legal_move_list = "\n".join(legal_move_list)

    prompt = f"""
    [no prose]
    [Output only the move in a JSON format with key: "move", value: WHATEVER_THE_MOST_LIKELY_MOVE_IS according to game history]
    You are a chess agent who can take on the persona of any player given their move history.
    You have been given the move history of a player who has played the following moves:
    {formatted_move_list}

    These are the possible legal moves for the next move:
    {formatted_legal_move_list}

    Understand the underlying patterns from the given game history and moves to make the best move for the state: {formatted_partial_sequence}
    Make a move using by looking into the patterns and the possible legal moves.
    Emphasis on the copying the play style of the player given the move history.
    """

    t1 = time.time()
    response = ollama.generate(
        model="gemma:2b",
        prompt=prompt
    )
    t2 = time.time()

    response = str(response.get("response")).strip()
    print(response)
    response = json.loads(response)
    predicted_move = response["move"]
    print(
        f"\nPredicted move: {predicted_move}\nProcessing time: {round(t2 - t1)} second(s)\n"
    )
    board.push_san(predicted_move)
    print(board)
    return predicted_move

    # gemini_response = model.generate_content(prompt)
    # gemini_response = gemini_response.text.strip()
    # gemini_response

    # if gemini_response in legal_move_list:
    #     print(f"Best move: {gemini_response}")
    #     board.push_san(gemini_response)
    # return gemini_response


def main():
    lichess_username = sys.argv[1]
    partial_sequence_list = sys.argv[2]

    # llm_model = init_gemini_model()
    game_history_df = get_game_history_df(lichess_username)
    compute_next_move(partial_sequence_list, game_history_df, None)


if __name__ == "__main__":
    main()
