// src/ChessGame.js
import React, { useState, useMemo } from "react";
import { Card, CardContent, Grid } from "@mui/material";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
// Local
import { BackgroundGradient } from "../components/ui/background-gradient";
import { HistoryOutlined, InsightsOutlined } from "@mui/icons-material";

function CustomAppBar() {
  return <div className="text-2xl mb-8 ml-4 mt-4">mirrormate.ai</div>;
}

function PaneTwoComponent() {
  const game = useMemo(() => new Chess(), []);
  const [gamePosition, setGamePosition] = useState(game.fen());

  // This function will be triggered when a piece is moved on the board
  function onDrop(sourceSquare, targetSquare, piece) {
    const move = game.move({
      from: sourceSquare,
      to: targetSquare,
      promotion: piece[1].toLowerCase() ?? "q",
    });
    setGamePosition(game.fen());

    // illegal move
    if (move === null) return false;

    // exit if the game is over
    if (game.isGameOver() || game.isDraw()) return false;

    // findBestMove();

    return true;
  }

  return (
    <div>
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
      <p className="text-xl mt-2">rootsec1</p>
    </div>
  );
}

function PaneThreeComponent() {
  return (
    <div className="flex flex-col h-[95%]">
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
    </div>
  );
}

export default function GamePage() {
  return (
    <div className="h-dvh p-4">
      <CustomAppBar />

      <Grid
        container
        sx={{ justifyContent: "space-around", display: "flex", flex: 1 }}
        spacing={1}
      >
        <Grid item lg={5.5}>
          <PaneTwoComponent />
        </Grid>

        <Grid item lg={5.5}>
          <PaneThreeComponent />
        </Grid>
      </Grid>
    </div>
  );
}
