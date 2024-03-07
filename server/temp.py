import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

# Sample data
# You should replace this with your dataset
# Format: list of moves sequences (each move represented as a string)
chess_moves_sequences = [['e4', 'e5', 'Nf3'], ['e4', 'e5', 'Nf3', 'Nc6'], ['e4', 'c5'], ['d4', 'd5', 'c4']]
next_moves = ['Nc6', 'Bb5', 'Nf3', 'e6']  # The next move after each sequence

# Convert moves to integer IDs
all_moves = set(sum(chess_moves_sequences, []) + next_moves)
move_to_id = {move: i for i, move in enumerate(all_moves)}
id_to_move = {i: move for move, i in move_to_id.items()}

# Prepare the data
X = [[move_to_id[move] for move in seq] for seq in chess_moves_sequences]
y = [move_to_id[move] for move in next_moves]

# One-hot encode the sequences for LSTM
encoder = OneHotEncoder(categories=[range(len(all_moves))])
X_encoded = [encoder.fit_transform(np.array(seq).reshape(-1, 1)) for seq in X]
y_encoded = encoder.fit_transform(np.array(y).reshape(-1, 1))

# Pad sequences to have the same length
max_sequence_length = max(len(seq) for seq in X_encoded)
X_padded = np.array([np.pad(seq, ((0, max_sequence_length - len(seq)), (0, 0)), 'constant') for seq in X_encoded])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_padded, y_encoded, test_size=0.2, random_state=42)

# Build the LSTM model
model = Sequential([
    LSTM(64, input_shape=(max_sequence_length, len(all_moves))),
    Dense(len(all_moves), activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=20, validation_data=(X_test, y_test))

# Predict the next move
def predict_next_move(sequence):
    sequence_ids = [move_to_id[move] for move in sequence]
    sequence_encoded = encoder.transform(np.array(sequence_ids).reshape(-1, 1))
    sequence_padded = np.pad(sequence_encoded, ((0, max_sequence_length - len(sequence_encoded)), (0, 0)), 'constant')
    sequence_reshaped = np.array([sequence_padded])
    prediction = model.predict(sequence_reshaped)
    predicted_move_id = np.argmax(prediction)
    return id_to_move[predicted_move_id]

# Example usage
print(predict_next_move(['e4', 'e5']))
