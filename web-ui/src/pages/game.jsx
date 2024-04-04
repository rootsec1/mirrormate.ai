// src/ChessGame.js
import {
  Card,
  CardContent,
  Chip,
  Grid,
  Snackbar,
  SnackbarContent,
} from "@mui/material";
import { Chess } from "chess.js";
import React, { useMemo, useState } from "react";
import { Chessboard } from "react-chessboard";
import { useLocation } from "react-router-dom";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import gfm from "remark-gfm";

// Local
import {
  CHESS_BOARD_ALL_SQUARES,
  getPromptForMoveAnalysis,
} from "../constants";
import { HistoryOutlined, InsightsOutlined } from "@mui/icons-material";
import { BackgroundGradient } from "../components/ui/background-gradient";
import { promptLLM } from "../util/llm";

function CustomAppBar() {
  return <div className="text-2xl ml-4 mt-2">mirrormate.ai</div>;
}

function PaneOneComponent({
  lichessUsernameTarget,
  usernameSelf,
  playAsColor,
  moveHistory,
  setMoveHistory,
  setError,
  setAnalysisText,
}) {
  const game = useMemo(() => new Chess(), []);
  const [gamePosition, setGamePosition] = useState(game.fen());

  function findKingPosition(game, color) {
    for (let square of CHESS_BOARD_ALL_SQUARES) {
      const piece = game.get(square);
      if (piece && piece.type === "k" && piece.color === color) {
        return square; // Return the square where the king of the specified color is located
      }
    }
    return null; // Return null if no king found (should never happen in a valid game)
  }

  async function predictNextMove(movesInSanList) {
    const movesInSanString = movesInSanList.join(" ");
    const endpointUrl = `/train/next-move/?lichess_username=${lichessUsernameTarget}&partial_sequence=${movesInSanString}`;
    let apiResponse = await axios.get(endpointUrl, null);
    apiResponse = await apiResponse.data;
    const predictedMoveInSan = apiResponse["predicted_move"];
    return predictedMoveInSan;
  }

  // This function will be triggered when a piece is moved on the board
  async function onDrop(sourceSquare, targetSquare, piece) {
    try {
      setError(null);
      const move = game.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: piece[1].toLowerCase() ?? "q",
      });

      // illegal move or game over
      if (move === null || game.isGameOver() || game.isDraw()) {
        return false; // Do not update the game position or move history
      }

      setGamePosition(game.fen());
      setMoveHistory((prev) => [...prev, move.san]); // Add the new move in SAN format to the history

      setAnalysisText("Analyzing");

      // Call API from backend to predict the opponent's move
      const predictedMoveInSan = await predictNextMove([
        ...moveHistory,
        move.san,
      ]);
      if (predictedMoveInSan) {
        // Now apply the predicted move to the game
        const predictedMove = game.move(predictedMoveInSan);

        // Check if the predicted move is legal
        if (predictedMove) {
          setGamePosition(game.fen()); // Update the position with the new move
          setMoveHistory((prev) => [...prev, predictedMoveInSan]); // Add the predicted move to history

          // Move analysis
          const movesInSanString = moveHistory.join(" ").trim();
          if (movesInSanString !== "") {
            const prompt = getPromptForMoveAnalysis(
              movesInSanString,
              playAsColor
            );
            const llmResponse = (await promptLLM(prompt)).trim();
            setAnalysisText(llmResponse);
          }
        } else {
          // Handle illegal predicted moves or other issues
          setError(`Predicted move is illegal: ${predictedMoveInSan}`);
        }
      }

      return true;
    } catch (error) {
      setError(error.message);
      return false;
    }
  }

  const isInCheck = game.isCheck(); // Check if the king is in check
  const isInCheckmate = game.isCheckmate(); // Check if the king is in checkmate

  // Determine the positions of the kings to highlight them if in check
  const whiteKingPosition = findKingPosition(game, "w");
  const blackKingPosition = findKingPosition(game, "b");

  // Assuming you have variables isInCheck and isInCheckmate that are already defined
  const kingPositions = {
    w: whiteKingPosition,
    b: blackKingPosition,
  };

  return (
    <div>
      <p className="text-xl mb-2 flex justify-center">
        {playAsColor === "Black" ? usernameSelf : lichessUsernameTarget}
      </p>{" "}
      <BackgroundGradient className="rounded-full p-1">
        <Card elevation={16} sx={{ backgroundColor: "transparent" }}>
          <Chessboard
            position={gamePosition}
            onPieceDrop={onDrop}
            customBoardStyle={{
              borderRadius: 16, // Apply rounded borders
              boxShadow: "0 5px 15px rgba(0, 0, 0, 0.5)", // Optional: adds shadow for depth
            }}
            customLightSquareStyle={{ backgroundColor: "white" }} // Adjust for your preferred light square color
            customDarkSquareStyle={{ backgroundColor: "#9575cd" }} // Adjust for your preferred dark square color (cyan-500)
            customSquareStyles={{
              ...(isInCheck &&
                kingPositions[game.turn()] && {
                  [kingPositions[game.turn()]]: { backgroundColor: "red" },
                }), // Highlight the king's position if in check
              ...(isInCheckmate &&
                kingPositions[game.turn()] && {
                  [kingPositions[game.turn()]]: { backgroundColor: "darkred" },
                }), // Highlight the king's position more if in checkmate
            }}
          />
        </Card>
      </BackgroundGradient>
      <p className="text-xl mt-2 flex justify-center">
        {playAsColor === "White" ? usernameSelf : lichessUsernameTarget}
      </p>
    </div>
  );
}

function PaneThreeComponent({ analysisText }) {
  return (
    <div className="flex flex-col h-[98%]">
      <Card
        elevation={16}
        className="flex-1"
        sx={{
          backgroundColor: "white",
          color: "black",
          borderRadius: 2,
          marginTop: "3%",
        }}
      >
        <CardContent>
          <span className="text-2xl font-medium">
            Move Analysis&nbsp;&nbsp;
            <InsightsOutlined fontSize="large" />
          </span>{" "}
          <br />
          <ReactMarkdown
            remarkPlugins={[gfm]}
            children={analysisText}
            components={{
              table: ({ node, ...props }) => (
                <table className="md-table" {...props} />
              ),
            }}
          />
        </CardContent>
      </Card>
    </div>
  );
}

function PaneTwoComponent({ moveHistory }) {
  function getMoveHistoryComponent() {
    return moveHistory.map((moveInSan, index) => (
      <Chip
        key={index}
        variant={index % 2 === 0 ? "filled" : "outlined"}
        label={moveInSan}
        sx={{
          color: index % 2 === 0 ? "black" : "white",
          fontSize: 16,
          border: 1,
          backgroundColor: index % 2 === 0 ? "white" : "#9575cd",
          marginRight: 2,
          marginBottom: 2,
        }}
      />
    ));
  }

  return (
    <div className="flex flex-col h-[98%]">
      <Card
        elevation={16}
        className="flex-1"
        sx={{
          backgroundColor: "white",
          color: "black",
          borderRadius: 2,
        }}
      >
        <CardContent>
          <span className="text-2xl font-medium">
            Move History&nbsp;
            <HistoryOutlined fontSize="large" />
          </span>

          <div id="move-history-container" className="mt-4">
            {getMoveHistoryComponent()}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function GamePage() {
  const location = useLocation();
  const [moveHistory, setMoveHistory] = useState([]); // New state variable for move history
  const [error, setError] = useState(null);
  const [analysisText, setAnalysisText] = useState(
    "Not enough data to analyze"
  ); // New state variable for analysis text

  const lichessUsernameTarget = location.state.lichess_username_target;
  const usernameSelf = location.state.username_self;
  const playAsColor = location.state.play_as_color;

  return (
    <div className="h-dvh p-4">
      <CustomAppBar />

      <Grid
        container
        sx={{ justifyContent: "space-around", display: "flex", flex: 1 }}
        spacing={1}
      >
        <Grid item lg={3}>
          <PaneThreeComponent analysisText={analysisText} />
        </Grid>

        <Grid item lg={5.5}>
          <PaneOneComponent
            lichessUsernameTarget={lichessUsernameTarget}
            usernameSelf={usernameSelf}
            playAsColor={playAsColor}
            moveHistory={moveHistory}
            setMoveHistory={setMoveHistory}
            setError={setError}
            setAnalysisText={setAnalysisText}
          />
        </Grid>

        <Grid item lg={3}>
          <PaneTwoComponent moveHistory={moveHistory} />
        </Grid>
      </Grid>

      {error && (
        <Snackbar
          className="backdrop-filter backdrop-blur-lg"
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          autoHideDuration={3000}
          open={error !== null}
          onClose={() => setError(null)}
          message={error}
        >
          <SnackbarContent
            sx={{ backgroundColor: "#e53935", color: "white", fontSize: 16 }}
            message={error}
          />
        </Snackbar>
      )}
    </div>
  );
}
