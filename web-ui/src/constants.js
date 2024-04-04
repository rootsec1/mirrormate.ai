export const API_URL = process.env.REACT_APP_API_URL;

// Define all squares manually if chess.js doesn't expose them
export const CHESS_BOARD_ALL_SQUARES = [
  "a1",
  "b1",
  "c1",
  "d1",
  "e1",
  "f1",
  "g1",
  "h1",
  "a2",
  "b2",
  "c2",
  "d2",
  "e2",
  "f2",
  "g2",
  "h2",
  "a3",
  "b3",
  "c3",
  "d3",
  "e3",
  "f3",
  "g3",
  "h3",
  "a4",
  "b4",
  "c4",
  "d4",
  "e4",
  "f4",
  "g4",
  "h4",
  "a5",
  "b5",
  "c5",
  "d5",
  "e5",
  "f5",
  "g5",
  "h5",
  "a6",
  "b6",
  "c6",
  "d6",
  "e6",
  "f6",
  "g6",
  "h6",
  "a7",
  "b7",
  "c7",
  "d7",
  "e7",
  "f7",
  "g7",
  "h7",
  "a8",
  "b8",
  "c8",
  "d8",
  "e8",
  "f8",
  "g8",
  "h8",
];

export function getPromptForMoveAnalysis(moves_in_san_str, playerColor) {
  const opponentColor = playerColor === "White" ? "Black" : "White";
  const firstOrSecondMove = playerColor === "White" ? "second" : "first";

  const promptTemplate = `
  This is the list of SAN moves on a chess board so far: ${moves_in_san_str}

  You are a chess grandmaster and a tutor. The goal is to understand the opponent's play style and behavior.
  I am the ${playerColor} player. Every alternative move starting from the ${firstOrSecondMove} move is my opponent's (${opponentColor}'s) move.
  Give me a short analysis that answers the following questions so that it guides me to beat my opponent.
  Generate the output in GitHub Flavored Markdown, fill it with tables of probabilities and more. Use percentages and numbers.
  Use all the features of markdown to give me a rich analysis.
  Use richly formatted bullet points in place of tables.

  Do not recommend any moves.
  Do not include "notes" or any other disclaimers.

  - Which opening is happening currently?
  - Which side is opponent trying to attack?
  - What is their play style?
  `;

  console.log(promptTemplate);

  return promptTemplate;
}
