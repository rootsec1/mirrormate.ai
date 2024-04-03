import chess
import pandas as pd

from stockfish import Stockfish

# Local
from constants import STOCKFISH_PATH
from llm_client import LLMClient
from scripts.util import make_prediction_using_model

__stockfish__ = Stockfish(STOCKFISH_PATH)


class ChessClient:
    move_list_in_san: list[str] = []
    move_list_in_uci: list[str] = []
    lichess_username: str = None
    llm_client: LLMClient = None

    def __init__(self, move_list_in_san: list[str], lichess_username: str):
        self.move_list_in_san = move_list_in_san
        self.move_list_in_uci = self.san_to_uci()
        self.lichess_username = lichess_username
        self.llm_client = LLMClient()

    def san_to_uci(self):
        # If no board is provided, create a new one
        board = chess.Board()
        uci_moves = []
        for san in self.move_list_in_san:
            # Convert the SAN move to a move object
            move = board.parse_san(san)
            # Convert the move object to UCI format
            uci = move.uci()
            uci_moves.append(uci)
            # Make the move on the board
            board.push(move)
        return uci_moves

    # Function to evaluate a sequence of moves using Stockfish
    def determine_stockfish_intelligence_level(self):
        # Reset the board to the initial position
        __stockfish__.set_position([])
        player_score = 0  # Initialize player score
        for move in self.move_list_in_uci:
            best_move = __stockfish__.get_best_move()
            if move == best_move:
                player_score += 1  # Increment score if the player's move matches Stockfish's best move
            __stockfish__.make_moves_from_current_position([move])
        # Calculate the intelligence level as a percentage
        intelligence_level = (
            player_score / len(self.move_list_in_uci)
        ) * 100 if self.move_list_in_uci else 20
        if intelligence_level > 12:
            intelligence_level -= 4
        return intelligence_level

    # Option A
    def cache_search(self, partial_sequence_str: str, game_history_df: pd.DataFrame):
        subset_df = game_history_df[
            game_history_df["input_sequence"] == partial_sequence_str
        ]
        if subset_df.empty:
            return None

        target_move = subset_df["target_move"].value_counts().idxmax()
        return {
            "predicted_move": target_move,
            "source": "cache"
        }

    # Option B
    def predict_using_model(self, partial_sequence_str: str, legal_move_set: set):
        result = make_prediction_using_model(
            partial_sequence_str,
            lichess_username=self.lichess_username
        )
        if result not in legal_move_set:
            raise ValueError("Illegal move by system")
        return {
            "predicted_move": result,
            "source": "model"
        }

    # Option C
    def stockfish_best_move_search(self):
        # Get stockfish intelligence level from partial_sequence which is a list of SAN moves
        intelligence_level = self.determine_stockfish_intelligence_level()
        __stockfish__.set_position(self.move_list_in_san)
        __stockfish__.set_skill_level(intelligence_level)
        # Get the best move from Stockfish
        best_move = __stockfish__.get_best_move()

        return {
            "predicted_move": best_move,
            "source": "stockfish"
        }

    def compute_next_move(self, game_history_df: pd.DataFrame) -> str:
        partial_sequence_str = " ".join(self.move_list_in_san).strip()

        # Setup Board
        board = chess.Board()
        for move in self.move_list_in_san:
            board.push_san(move)

        # Option A = Cache search
        result = self.cache_search(partial_sequence_str, game_history_df)
        if result is not None:
            return result

        # Get legal moves
        legal_move_set = board.legal_moves
        legal_move_set = set([board.san(move) for move in legal_move_set])

        try:
            # Option B = Model predictions
            result = self.predict_using_model(
                partial_sequence_str,
                legal_move_set
            )
            if result is not None:
                return result

        except Exception as ex:
            print(ex)
            # Option C = Stockfish
            result = self.stockfish_best_move_search()
            if result is not None:
                return result
