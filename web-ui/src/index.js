// Import the createTheme and ThemeProvider components from @mui/material
import { createTheme, ThemeProvider } from "@mui/material";
// Import the axios library for making HTTP requests
import axios from "axios";
// Import the React library
import React from "react";
// Import the ReactDOM library for rendering React components
import ReactDOM from "react-dom/client";
// Import the createBrowserRouter and RouterProvider components from react-router-dom for routing
import { createBrowserRouter, RouterProvider } from "react-router-dom";

// Local
// Import the API_URL constant from the local constants module
import { API_URL } from "./constants";
// Import the local index.css file for global styles
import "./index.css";
// Import the GamePage component from the local pages/game module
import GamePage from "./pages/game";
// Import the SplashPage component from the local pages/splash module
import SplashPage from "./pages/splash";
// Import the themeOptions object from the local theme module
import { themeOptions } from "./theme";

// Set the default base URL for axios to the API_URL
axios.defaults.baseURL = API_URL;

// Create a theme using the themeOptions object
const appTheme = createTheme(themeOptions);

// Create a browser router with two routes: one for the splash page and one for the game page
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

// Get the root element from the DOM
const root = ReactDOM.createRoot(document.getElementById("root"));
// Render the app inside the root element, with the ThemeProvider and RouterProvider wrapping the app
root.render(
  <React.StrictMode>
    <ThemeProvider theme={appTheme}>
      <RouterProvider router={router} />
    </ThemeProvider>
  </React.StrictMode>
);
