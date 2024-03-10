import { createTheme, ThemeProvider } from "@mui/material";
import axios from "axios";
import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

// Local
import { API_URL } from "./constants";
import "./index.css";
import GamePage from "./pages/game";
import SplashPage from "./pages/splash";
import { themeOptions } from "./theme";

// Point the axios base URL to the API_URL
axios.defaults.baseURL = API_URL;

const appTheme = createTheme(themeOptions);

const router = createBrowserRouter([
  {
    path: "/",
    element: <SplashPage />,
  },
  {
    path: "game",
    element: <GamePage />,
  },
]);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={appTheme}>
      <RouterProvider router={router} />
    </ThemeProvider>
  </React.StrictMode>
);
