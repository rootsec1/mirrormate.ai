import pandas as pd
import chess
import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import LabelEncoder

# Initialize label encoder and hyperparameters
label_encoder = LabelEncoder()
NUM_EPOCHS = 25
BATCH_SIZE = 12
LEARNING_RATE = 0.001

# Define a PyTorch Dataset for chess data


class ChessDataset(Dataset):
    """A PyTorch Dataset for chess data."""

    def __init__(self, features, labels):
        self.features = features
        self.labels = labels

    def __len__(self):
        return len(self.features)

    def __getitem__(self, index):
        return self.features[index], self.labels[index]

# Define a PyTorch neural network for chess move prediction


class ChessNN(nn.Module):
    """A PyTorch neural network for chess move prediction."""

    def __init__(self, input_dim, output_dim):
        super(ChessNN, self).__init__()
        # Define the network architecture
        self.layer1 = nn.Linear(input_dim, 256)
        self.layer2 = nn.Linear(256, 128)
        self.output_layer = nn.Linear(128, output_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        # Define the forward pass
        x = self.relu(self.layer1(x))
        x = self.dropout(x)
        x = self.relu(self.layer2(x))
        x = self.dropout(x)
        x = self.output_layer(x)
        return x

# Function to convert the board to a flat list


def board_to_flat_list(board):
    """Convert a chess board to a flat list."""
    board_string = board.__str__()
    rows = board_string.split("\n")
    flat_list = []
    for row in rows:
        pieces = row.split(" ")
        flat_list.extend(pieces)
    flat_list = [None if piece == "." else piece for piece in flat_list]
    return flat_list

# Function to get the vocabulary of the chess board


def get_vocabulary() -> tuple[dict, dict]:
    """Get the vocabulary of the chess board."""
    fresh_chess_board = chess.Board()
    unique_characters = list(set(fresh_chess_board.board_fen()))
    unique_characters = [char for char in unique_characters if char.isalpha()]
    unique_characters.sort()
    vocabulary_dict = {char: i+1 for i, char in enumerate(unique_characters)}
    vocabulary_dict["EMPTY"] = -1
    reverse_vocabulary_dict = {i: char for char, i in vocabulary_dict.items()}
    return vocabulary_dict, reverse_vocabulary_dict

# Function to encode the DataFrame using the vocabulary


def encode_df(df: pd.DataFrame, vocabulary_dict: dict) -> pd.DataFrame:
    """Encode the DataFrame using the vocabulary."""
    df = df.fillna("EMPTY")
    df = df.map(lambda x: vocabulary_dict[x] if x in vocabulary_dict else x)
    return df

# Function to decode the model prediction


def decode_model_prediction(prediction_list: list, reverse_vocabulary_dict: dict) -> list[str]:
    """Decode the model prediction."""
    ret_list = [reverse_vocabulary_dict[i] for i in prediction_list]
    ret_list = [None if x == "EMPTY" else x for x in ret_list]
    return ret_list

# Function to create the dataset


def create_dataset(lichess_username: str) -> pd.DataFrame:
    """Create the dataset."""
    data_df = pd.read_csv(f"../data/raw/games_{lichess_username}.csv")
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

# Function to split the dataset into train and validation


def get_dataset_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split the dataset into train and validation."""
    df = df.rename(columns={0: "game_id", len(df.columns)-1: "target_move"})

    X = df.drop(['target_move', 'game_id'], axis=1)
    y = df['target_move']
    y_integers = label_encoder.fit_transform(y.values)

    gss = GroupShuffleSplit(test_size=0.2, n_splits=1, random_state=0)
    train_idx, val_idx = next(gss.split(X, y, groups=df['game_id']))

    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y_integers[train_idx], y_integers[val_idx]

    print("Shapes:", X_train.shape, X_val.shape, y_train.shape, y_val.shape)
    return X_train, X_val, y_train, y_val

# Function to train the model


def train_model(df: pd.DataFrame):
    """Train the model."""
    X_train, X_val, y_train, y_val = get_dataset_split(df)

    X_train_tensor = torch.FloatTensor(X_train.values)
    y_train_tensor = torch.LongTensor(y_train)
    X_val_tensor = torch.FloatTensor(X_val.values)
    y_val_tensor = torch.LongTensor(y_val)

    train_dataset = ChessDataset(X_train_tensor, y_train_tensor)
    val_dataset = ChessDataset(X_val_tensor, y_val_tensor)
    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=False)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

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

# Function to save the model


def save_model(model: ChessNN, model_name: str):
    """Save the model."""
    torch.save(model, model_name)

# Main function


def main():
    """Main function."""
    lichess_username = "ritutoshniwal"
    vocabulary_dict, reverse_vocabulary_dict = get_vocabulary()

    dataset_df = create_dataset(lichess_username)
    dataset_df = encode_df(dataset_df, vocabulary_dict)

    print(dataset_df.describe())

    model = train_model(dataset_df)

    save_model(model, "../models/chess_nn_model.pth")


# Run the main function if this script is run as the main module
if __name__ == "__main__":
    main()
