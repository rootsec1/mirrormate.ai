import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
} from "@mui/material";
import axios from "axios";
import { motion } from "framer-motion";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// Local
import { LampContainer } from "../components/ui/lamp";
import { MovingBorderButton } from "../components/ui/moving-border";
import { MultiStepLoader as Loader } from "../components/ui/multi-step-loader";
import { TextGenerateEffect } from "../components/ui/text-generate-effect";

// Constants
const LOADER_DURATION = 2000;

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
          onSubmit(formJson["lichess_username"]);
        },
      }}
    >
      <DialogTitle>Enter opponent's Lichess username</DialogTitle>
      <DialogContent>
        <DialogContentText>
          To clone a persona, you need to enter the Lichess username of the
          opponent you want to clone.
        </DialogContentText>
        <TextField
          autoFocus
          required
          margin="dense"
          id="name"
          name="lichess_username"
          label="Lichess username"
          type="text"
          fullWidth
          variant="standard"
        />
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

export default function SplashPage() {
  const navigate = useNavigate();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [username, setUsername] = useState(null);

  async function triggerClonePersonaForUsername(lichessUsername) {
    const endpointUrl = `/train/persona/${lichessUsername}`;
    const apiResponse = await axios.get(endpointUrl);
    const apiResponseData = apiResponse.data;
    const cloningStatus = apiResponseData["status"];
    if (cloningStatus === "CLONING_COMPLETE") {
      navigate("game", {
        state: {
          lichessUsername,
        },
      });
    } else {
      setUsername(null);
    }
  }

  function onGetStartedButtonClick() {
    setIsDialogOpen(true);
  }

  function onSubmitLichessUsernameForm(lichessUsername) {
    setIsDialogOpen(false);
    setUsername(lichessUsername);
    triggerClonePersonaForUsername(lichessUsername);
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
