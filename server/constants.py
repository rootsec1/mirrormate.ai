"""Constants for the project."""
import os

LICHESS_API_TOKEN = os.environ["LICHESS_API_TOKEN"]
DATA_DIRECTORY = "data"

LLM_NEXT_MOVE_PROMPT = """
Output only a single JSON object with the key "move" and the value as the next move to make.
Be as aggressive as possible in your move selection. Play towards the center of the board as much as possible.

You are a chess copy agent who can take on the persona of any player given their move history.
You have been given the move history of a player who has played the following moves:
{formatted_move_list}

These are the possible legal moves for the next move.
Strictly include and output only one of these moves as the next move to make:
{formatted_legal_move_list}

Understand the underlying patterns from the following game state to make the best move:
{formatted_partial_sequence}

Only output the JSON object with the key "move" and the value as the next move to make. Nothing else.
No explanation or reasoning is required. Only the next move is required.
"""
