# mirrormate.ai

Play a game of chess against an AI clone of your opponent enabling you to understand their play style, strengths and weaknesses before the actual game.

## Screenshots
<img width="1242" alt="Screenshot 2024-04-03 at 1 44 39 AM" src="https://github.com/rootsec1/mirrormate.ai/assets/20264867/462216c3-903c-4914-aa0a-938e9c551b1e">
<img width="1470" alt="Screenshot 2024-04-03 at 2 00 17 AM" src="https://github.com/rootsec1/mirrormate.ai/assets/20264867/2b2c9214-df1c-4e16-b277-517e5b8f3f55">

## Overview

Mirromate is an innovative web-based chess application designed to help highly-ranked chess players prepare for matches by studying their opponents' historical game data. This tool significantly reduces the time and effort required to analyze rivals' past games and styles. By leveraging game histories from platforms like lichess.org, MirrorMate.ai creates a "clone" of an opponent, allowing users to engage with this model to better understand their strategies and tactics.

## Build Status

[![Netlify Status](https://api.netlify.com/api/v1/badges/21d76bea-8afa-47d2-a863-0a8539be4cc1/deploy-status)](https://app.netlify.com/sites/mirrormate-ai/deploys)

## Directory Structure

```
├── README.md                             # Documentation of the project
├── data                                  # Data files for training and analysis
│   ├── processed                         # Processed data ready for model consumption
│   │   ├── sequence_target_map_*.csv     # Mapping of chess sequences to target moves
│   │   └── vocabulary_san.txt            # SAN (Standard Algebraic Notation) vocabulary
│   └── raw                               # Raw data files, possibly unprocessed game data
│       └── games_*.csv                   # Collection of chess games data
├── models                                # Trained model files and related information
│   └── ritutoshniwal                     # Model related to the user 'ritutoshniwal'
│       ├── label_encoder.pickle          # Encoded labels for the model
│       ├── model_arch.json               # Model architecture in JSON format
│       ├── model_weights.h5              # HDF5 file containing model weights
│       └── tokenizer.pickle              # Tokenizer for converting text to tokens
├── notebooks                             # Jupyter notebooks for exploration and testing
│   ├── dl_*.ipynb                        # Various deep learning model notebooks
│   ├── generate_dataset.ipynb            # Notebook for dataset generation
│   ├── main_approach_dl_gru.ipynb        # Main approach using a GRU based model
│   ├── naive_approach.ipynb              # Notebook for a simpler approach
│   └── non_deep_learning_approach.ipynb  # Non-deep learning model approach
├── server                                # Backend server configuration and scripts
│   ├── README.md                         # Server documentation
│   ├── chess_client.py                   # Client for interacting with the chess server
│   ├── constants.py                      # Server-side constants
│   ├── llm_client.py                     # Client for interacting with language models
│   ├── main.py                           # Main server script
│   ├── requirements.txt                  # Server dependencies
│   └── routes                            # Route definitions for server
│       ├── lichess.py                    # Lichess API route
│       └── train.py                      # Training route
├── scripts                               # Utility scripts for various tasks
│   ├── __init__.py                       # Makes scripts a Python module
│   ├── deep_learning_approach.py         # Deep learning related scripts
│   ├── make_dataset.py                   # Script for creating datasets
│   ├── make_vocabulary.py                # Script for generating vocabulary
│   ├── non_deep_learning_approach_model.py # Script for non-deep learning models
│   └── util.py                           # Utility functions
├── web-ui                                # Frontend web user interface
│   ├── README.md                         # UI documentation
│   ├── package*.json                     # npm package configuration
│   ├── public                            # Public assets for the web UI
│   │   ├── *                             # Icons, manifests, and other static files
│   │   └── index.html                    # Entry HTML file
│   └── src                               # Source code for the web UI
│       ├── components                    # Reusable UI components
│       │   └── ui                        # Specific UI component implementations
│       ├── constants.js                  # UI constants
│       ├── index.*                       # Main entry points for styling and scripting
│       ├── pages                         # Individual pages/components for routing
│       ├── theme.js                      # Theme configuration for styling
│       ├── util                          # Utility functions for the frontend
│       └── tailwind.config.js            # TailwindCSS configuration
```

## How to setup and run locally
1. Clone the repo: `git@github.com:rootsec1/mirrormate.ai.git`
2. Go into the `server` folder, create a virtual environment and install all dependencies
```
cd server
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```
3. Before you start the server, ensure you set the following environment variables: `LICHESS_API_TOKEN` and `GEMINI_API_KEY`
4. Install `stockfish` using `brew install stockfish` (for other platforms, refer [this page](https://stockfishchess.org/download/)) and change `STOCKFISH_PATH` accordingly in the `server/constants.py` file
3. To start the FastAPI server, run: `uvicorn main:app --host 0.0.0.0 --port 6942`
4. Now, on another terminal, go into the project folder and then change directory to the `web-ui` folder using: `cd web-ui`
5. Install all the necessary dependencies for the React app using: `npm i`
6. Next, run on the frontend using: `npm start`, this serves the frontend on [http://localhost:3000](http://localhost:3000)

## Model Architecture
MirrorMate.ai employs a hybrid approach, combining a cache query system, a Gated Recurrent Unit (GRU) model, and the Stockfish game engine. This multi-tiered approach ensures robust and strategic gameplay prediction.

### Non-Deep Learning Approach
- **Random Forest Model**: Uses 64 features representing each square on the chessboard, with each piece encoded as an integer. The model learns from various board states to predict the next move.

### Naive Approach
- **GRU Model**: A simpler model with 1.2M parameters, a vocabulary size of 178, and 400 GRU units. It includes dropout regularization and utilizes categorical crossentropy loss with the Adam optimizer.

### Main Approach (Deep Neural Network)
- **In-memory Cache Query**: A quick retrieval system that searches for move sequences in a pre-stored cache.
- **GRU Model**: Employs the naive approach's GRU model to predict the next move when the cache query is unsuccessful.
- **Stockfish Integration**: For scenarios where the model predicts illegal moves, Stockfish assesses the user's play level to suggest a move that matches the user's skill.
<img width="523" alt="Screenshot 2024-04-23 at 3 18 56 PM" src="https://github.com/rootsec1/mirrormate.ai/assets/20264867/90389b50-9b85-4f2c-8808-3541f264d266">


## Evaluation Metric
Traditional accuracy metrics proved insufficient for this project due to the complex nature of legal and strategic move generation. Instead, a more human-centric evaluation was employed:

- **Human Judge**: The true efficacy of the model is judged by the cloned players themselves, comparing the model's predictions with the players' actual moves.
- **Accuracy Scores**:
    - Random Forest: 96%
    - GRU (naive): 76.4%
    - Cache query + GRU + Stockfish: 88.2%
This human-involved approach led to the finding that the combination of caching mechanisms, the GRU model, and Stockfish engine fallback provides the most accurate move predictions, with an average accuracy of 79.3% across all games.

## Results and Conclusion

The integration of a caching system with the predictive power of a GRU model and the strategic depth of the Stockfish engine culminated in a robust solution that closely mimics an opponent's play style. Future work includes optimizing ad-hoc training processes and improving user notification systems.

