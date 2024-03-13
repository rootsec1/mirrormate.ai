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
// Local
import { HistoryOutlined, InsightsOutlined } from "@mui/icons-material";
import { BackgroundGradient } from "../components/ui/background-gradient";

function CustomAppBar() {
  return <div className="text-2xl ml-4 mt-2">mirrormate.ai</div>;
}

function PaneOneComponent({
  lichessUsernameTarget,
  usernameSelf,
  playAsColor,
  setMoveHistory,
  setError,
}) {
  const game = useMemo(() => new Chess(), []);
  const [gamePosition, setGamePosition] = useState(game.fen());

  // This function will be triggered when a piece is moved on the board
  function onDrop(sourceSquare, targetSquare, piece) {
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

      return true;
    } catch (error) {
      setError(error.message);
      return false;
    }
  }

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
          />
        </Card>
      </BackgroundGradient>
      <p className="text-xl mt-2 flex justify-center">
        {playAsColor === "White" ? usernameSelf : lichessUsernameTarget}
      </p>
    </div>
  );
}

function PaneTwoComponent({ moveHistory, error, setError }) {
  function getMoveHistoryComponent() {
    return moveHistory.map((moveInSan, index) => (
      <Chip
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
        </CardContent>
      </Card>

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

export default function GamePage() {
  const location = useLocation();
  const [moveHistory, setMoveHistory] = useState([]); // New state variable for move history
  const [error, setError] = useState(null);

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
        <Grid item lg={5.5}>
          <PaneOneComponent
            lichessUsernameTarget={lichessUsernameTarget}
            usernameSelf={usernameSelf}
            playAsColor={playAsColor}
            setMoveHistory={setMoveHistory}
            setError={setError}
          />
        </Grid>

        <Grid item lg={5.5}>
          <PaneTwoComponent
            moveHistory={moveHistory}
            error={error}
            setError={setError}
          />
        </Grid>
      </Grid>
    </div>
  );
}
