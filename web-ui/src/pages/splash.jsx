import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  TextField,
} from "@mui/material";
import axios from "axios";
import { motion } from "framer-motion";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// Importing local components
import { LampContainer } from "../components/ui/lamp";
import { MovingBorderButton } from "../components/ui/moving-border";
import { MultiStepLoader as Loader } from "../components/ui/multi-step-loader";
import { TextGenerateEffect } from "../components/ui/text-generate-effect";

// Constants
const LOADER_DURATION = 3000;

/**
 * Function to get loading states
 * @param {string} lichessUsername - The username on Lichess
 * @returns {Array} - An array of loading states
 */
const getLoadingStates = (lichessUsername) => [
  {
    text: `Looking up “${lichessUsername}” on Lichess`,
  },
  {
    text: "Fetching game history and moves in each game",
  },
  {
    text: "Analyzing moves and building persona",
  },
  {
    text: `Cloning ${lichessUsername}`,
  },
];

/**
 * Component for Lichess username input dialog
 * @param {Object} props - The properties passed to the component
 * @param {boolean} props.isOpen - Whether the dialog is open
 * @param {Function} props.setIsOpen - Function to set whether the dialog is open
 * @param {Function} props.onSubmit - Function to handle form submission
 */
function LichessUsernameInputDialogComponent({ isOpen, setIsOpen, onSubmit }) {
  return (
    <Dialog
      open={isOpen}
      onClose={() => setIsOpen(false)}
      PaperProps={{
        component: "form",
        onSubmit: (event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);
          const formJson = Object.fromEntries(formData.entries());
          onSubmit(formJson);
        },
      }}
    >
      <DialogTitle>Enter opponent's Lichess username</DialogTitle>
      <DialogContent>
        <DialogContentText>
          To clone a persona, you need to enter the Lichess username of the
          opponent you want to clone.
        </DialogContentText>

        <FormControl fullWidth>
          <TextField
            autoFocus
            required
            margin="dense"
            id="name"
            name="username_self"
            label="Your username"
            type="text"
            fullWidth
            variant="standard"
          />
          <TextField
            autoFocus
            required
            margin="dense"
            id="name"
            name="lichess_username_target"
            label="Target Lichess username to clone"
            type="text"
            fullWidth
            variant="standard"
          />
          Cloned Models: "ritutoshniwal"
          <FormLabel id="row-radio-buttons-group-label" className="mt-4">
            Play as
          </FormLabel>
          <RadioGroup
            row
            aria-labelledby="row-radio-buttons-group-label"
            name="play_as_color"
            value={"White"}
          >
            <FormControlLabel value="White" control={<Radio />} label="White" />
            <FormControlLabel value="Black" control={<Radio />} label="Black" />
          </RadioGroup>
        </FormControl>
      </DialogContent>
      <DialogActions>
        <Button color="secondary" onClick={() => setIsOpen(false)}>
          Cancel
        </Button>
        <Button type="submit">Clone persona</Button>
      </DialogActions>
    </Dialog>
  );
}

/**
 * Splash page component
 */
export default function SplashPage() {
  const navigate = useNavigate();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [username, setUsername] = useState(null);

  /**
   * Function to trigger clone persona for username
   * @param {Object} formJson - The form data in JSON format
   */
  async function triggerClonePersonaForUsername(formJson) {
    const lichessUsername = formJson["lichess_username_target"];

    const endpointUrl = `/train/persona/${lichessUsername}`;
    const apiResponse = await axios.get(endpointUrl);
    const apiResponseData = apiResponse.data;
    const cloningStatus = apiResponseData["status"];
    if (cloningStatus === "CLONING_COMPLETE") {
      navigate("game", {
        state: formJson,
      });
    } else {
      setUsername(null);
    }
  }

  /**
   * Function to handle get started button click
   */
  function onGetStartedButtonClick() {
    setIsDialogOpen(true);
  }

  /**
   * Function to handle Lichess username form submission
   * @param {Object} formJson - The form data in JSON format
   */
  function onSubmitLichessUsernameForm(formJson) {
    setIsDialogOpen(false);
    const lichessUsername = formJson["lichess_username_target"];
    setUsername(lichessUsername);
    // Run function after 10 seconds
    setTimeout(() => {
      triggerClonePersonaForUsername(formJson);
    }, LOADER_DURATION * 5);
  }

  return (
    <div>
      <Loader
        loadingStates={getLoadingStates(username)}
        loading={username !== null}
        duration={LOADER_DURATION}
        loop={false}
      />

      <LampContainer>
        <motion.h1
          initial={{ opacity: 0.7, y: 30 }}
          whileInView={{ opacity: 1, y: -80 }}
          transition={{
            delay: 0.5,
            duration: 2,
            ease: "easeInOut",
          }}
          className="bg-gradient-to-br from-slate-300 to-slate-500 py-4 bg-clip-text text-center text-4xl font-medium tracking-tight text-transparent md:text-7xl"
        >
          <p className="text-white">mirrormate.ai</p>
        </motion.h1>

        <TextGenerateEffect
          words="Duplicate and Dominate your competition in a game of Chess."
          className="text-3xl font-extralight"
        />
      </LampContainer>

      <div
        onClick={onGetStartedButtonClick}
        className="absolute top-2/3 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center"
      >
        <MovingBorderButton className="text-xl">Get started</MovingBorderButton>
      </div>

      <LichessUsernameInputDialogComponent
        isOpen={isDialogOpen}
        setIsOpen={setIsDialogOpen}
        onSubmit={onSubmitLichessUsernameForm}
      />
    </div>
  );
}
