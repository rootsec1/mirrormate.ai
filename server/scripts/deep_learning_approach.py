import pandas as pd
import numpy as np
import chess
import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler, LabelEncoder


label_encoder = LabelEncoder()
NUM_EPOCHS = 25
BATCH_SIZE = 12
LEARNING_RATE = 0.001


# Dataset and DataLoader
class ChessDataset(Dataset):
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels

    def __len__(self):
        return len(self.features)

    def __getitem__(self, index):
        return self.features[index], self.labels[index]


# Model definition
class ChessNN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(ChessNN, self).__init__()
        # Simplified network architecture
        self.layer1 = nn.Linear(input_dim, 256)  # Reduced from 512 to 256
        self.layer2 = nn.Linear(256, 128)  # A new, smaller intermediate layer
        # Output layer remains the same
        self.output_layer = nn.Linear(128, output_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)  # Reduced dropout rate

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.dropout(x)
        x = self.relu(self.layer2(x))
        x = self.dropout(x)
        x = self.output_layer(x)
        return x


# Function to convert the board to a flat list
def board_to_flat_list(board):
    # Get the board as a string in ASCII format
    board_string = board.__str__()
    # Split the board string into rows
    rows = board_string.split("\n")
    # Initialize an empty list to store the flat board
    flat_list = []
    # Iterate through each row
    for row in rows:
        # Split the row by spaces to get individual pieces
        pieces = row.split(" ")
        # Extend the flat list with the pieces
        flat_list.extend(pieces)

    # Replace "." with None
    flat_list = [None if piece == "." else piece for piece in flat_list]
    return flat_list


# Vocabulary
def get_vocabulary() -> tuple[dict, dict]:
    fresh_chess_board = chess.Board()
    # Get all unique characters in fresh_chess_board
    unique_characters = list(set(fresh_chess_board.board_fen()))
    unique_characters = [char for char in unique_characters if char.isalpha()]
    unique_characters.sort()
    vocabulary_dict = {char: i+1 for i, char in enumerate(unique_characters)}
    vocabulary_dict["EMPTY"] = -1
    reverse_vocabulary_dict = {i: char for char, i in vocabulary_dict.items()}
    return vocabulary_dict, reverse_vocabulary_dict


# For all values in X, transform string to int using vocabulary_dict
def encode_df(df: pd.DataFrame, vocabulary_dict: dict) -> pd.DataFrame:
    df = df.fillna("EMPTY")
    df = df.map(lambda x: vocabulary_dict[x] if x in vocabulary_dict else x)
    return df


def decode_model_prediction(prediction_list: list, reverse_vocabulary_dict: dict) -> list[str]:
    ret_list = [reverse_vocabulary_dict[i] for i in prediction_list]
    # If ret_list contains "EMPTY", replace it with None
    ret_list = [None if x == "EMPTY" else x for x in ret_list]
    return ret_list


# Create dataset
def create_dataset(lichess_username: str) -> pd.DataFrame:
    data_df = pd.read_csv(f"data/raw/games_{lichess_username}.csv")
    output_df = pd.DataFrame()
    game_list = []

    for _, row in data_df.iterrows():
        game_id = row.get("game_id")
        white_player = row.get("white_player")
        move_list = row.get("move_list")

        if isinstance(move_list, float):
            continue

        move_list = move_list.split(" ")

        generator_start_index = 0 if white_player == lichess_username else 1
        for move_idx in range(generator_start_index, len(move_list), 2):
            target_move = move_list[move_idx]
            input_sequence_list = move_list[:move_idx]

            board = chess.Board()
            for input_move in input_sequence_list:
                board.push_san(input_move)

            board_flat_list = [game_id]
            board_flat_list.extend(board_to_flat_list(board))
            board_flat_list.append(target_move)
            game_list.append(board_flat_list)

    output_df = pd.DataFrame(game_list)
    return output_df


# Split dataset into train and validation
def get_dataset_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Rename first col to game_id and last col to target_move
    df = df.rename(columns={0: "game_id", len(df.columns)-1: "target_move"})

    # Assuming df is your DataFrame and has columns for features and 'game_id'
    X = df.drop(['target_move', 'game_id'], axis=1)  # Features
    y = df['target_move']
    # Fit and transform the 'target_move' to integer
    y_integers = label_encoder.fit_transform(y.values)

    # Use GroupShuffleSplit to keep games together
    gss = GroupShuffleSplit(test_size=0.2, n_splits=1, random_state=0)
    train_idx, val_idx = next(gss.split(X, y, groups=df['game_id']))

    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y_integers[train_idx], y_integers[val_idx]

    print("Shapes:", X_train.shape, X_val.shape, y_train.shape, y_val.shape)
    return X_train, X_val, y_train, y_val


# Train model
def train_model(df: pd.DataFrame):
    X_train, X_val, y_train, y_val = get_dataset_split(df)

    # Convert to PyTorch tensors
    X_train_tensor = torch.FloatTensor(X_train.values)
    y_train_tensor = torch.LongTensor(y_train)
    X_val_tensor = torch.FloatTensor(X_val.values)
    y_val_tensor = torch.LongTensor(y_val)

    train_dataset = ChessDataset(X_train_tensor, y_train_tensor)
    val_dataset = ChessDataset(X_val_tensor, y_val_tensor)
    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=False)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Assuming the input dimension is the number of features from your board states,
    # and output_dim is the number of unique chess moves.
    input_dim = int(X_train.shape[1])
    output_dim = int(df.iloc[:, -1:].nunique().values[0])

    model = ChessNN(input_dim=input_dim, output_dim=output_dim)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(
        optimizer,
        step_size=5,
        gamma=0.1,
        verbose=True
    )

    model.train()
    for epoch in range(NUM_EPOCHS):
        for features, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            scheduler.step()
        print(f'Epoch {epoch+1}/{NUM_EPOCHS}, Loss: {loss.item()}')

    model.eval()
    total = 0
    correct = 0
    with torch.no_grad():
        for features, labels in val_loader:
            outputs = model(features)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    print(f'Accuracy: {100 * correct / total}%')
    return model


def save_model(model: ChessNN, model_name: str):
    torch.save(model, model_name)


def main():
    lichess_username = "ritutoshniwal"
    vocabulary_dict, reverse_vocabulary_dict = get_vocabulary()

    dataset_df = create_dataset(lichess_username)
    dataset_df = encode_df(dataset_df, vocabulary_dict)

    print(dataset_df.describe())

    model = train_model(dataset_df)

    save_model(model, "models/chess_nn_model.pth")


if __name__ == "__main__":
    main()
