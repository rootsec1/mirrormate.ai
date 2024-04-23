import re
import chess
import pandas as pd

from stockfish import Stockfish

# Local
from constants import STOCKFISH_PATH
from llm_client import LLMClient
from scripts.util import make_prediction_using_model

# Initialize Stockfish with the given path
__stockfish__ = Stockfish(STOCKFISH_PATH)


class ChessClient:
    """
    A client to handle chess game operations, including move conversions, 
    determining intelligence level, caching, predicting moves, and interacting with Stockfish.
    """

    move_list_in_san: list[str] = []  # List of moves in Standard Algebraic Notation (SAN)
    move_list_in_uci: list[str] = []  # List of moves in Universal Chess Interface (UCI)
    lichess_username: str = None  # Username of the player on Lichess
    llm_client: LLMClient = None  # Client for Lichess Ladder Monitor (LLM)

    def __init__(self, move_list_in_san: list[str], lichess_username: str):
        """
        Initialize the ChessClient with a list of moves in SAN and a Lichess username.
        """
        self.move_list_in_san = move_list_in_san
        self.move_list_in_uci = self.san_to_uci()
        self.lichess_username = lichess_username
        self.llm_client = LLMClient()

    def san_to_uci(self):
        """
        Convert a list of moves from Standard Algebraic Notation (SAN) to Universal Chess Interface (UCI).
        """
        # If no board is provided, create a new one
        board = chess.Board()
        uci_moves = []
        for san in self.move_list_in_san:
            san = san.strip()
            if san == "":
                continue
            # Convert the SAN move to a move object
            move = board.parse_san(san)
            # Convert the move object to UCI format
            uci = move.uci()
            uci_moves.append(uci)
            # Make the move on the board
            board.push(move)
        return uci_moves

    def determine_stockfish_intelligence_level(self):
        """
        Evaluate a sequence of moves using Stockfish and determine the intelligence level of the player.
        """
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

    def cache_search(self, partial_sequence_str: str, game_history_df: pd.DataFrame):
        """
        Search for a partial sequence of moves in the game history cache.
        """
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

    def predict_using_model(self, partial_sequence_str: str, legal_move_set: set):
        """
        Predict the next move using a trained model.
        """
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

    def stockfish_best_move_search(self):
        """
        Determine the best move according to Stockfish.
        """
        # Get stockfish intelligence level from partial_sequence which is a list of SAN moves
        intelligence_level = self.determine_stockfish_intelligence_level()
        __stockfish__.set_position(self.move_list_in_uci)
        __stockfish__.set_skill_level(intelligence_level)
        # Get the best move from Stockfish
        best_move = __stockfish__.get_top_moves(1)[0].get("Move")

        return {
            "predicted_move": best_move,
            "source": "stockfish"
        }

    def compute_next_move(self, game_history_df: pd.DataFrame) -> str:
        """
        Compute the next move using a combination of cache search, model prediction, and Stockfish.
        """
        partial_sequence_str = " ".join(self.move_list_in_san).strip()
        # Remove all special chars from the SAN moves except space (" ") and hyphen ("-")
        partial_sequence_str = re.sub(r"[^a-zA-Z0-9\s-]", "", partial_sequence_str)

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