"""Constants for the project."""
import os

LICHESS_API_TOKEN = os.environ["LICHESS_API_TOKEN"]
DATA_DIRECTORY = "data"

LLM_NEXT_MOVE_PROMPT = """
Output only a single JSON object with the key "move" and the value as the next move to make.

You are a chess copy agent who can take on the persona of any player given their move history.
You have been given the move history of a player who has played the following moves:
{formatted_move_list}

These are the possible legal moves for the next move:
{formatted_legal_move_list}

Understand the underlying patterns from the given game history to make the best move for the sequence:
{formatted_partial_sequence}

Only output the JSON object with the key "move" and the value as the next move to make. Nothing else.
No explanation or reasoning is required. Only the next move is required.
"""
