def create_san_vocabulary():
    """
    Creates a vocabulary of Standard Algebraic Notation (SAN) chess moves.

    Returns:
        list: A list of unique SAN chess moves.
    """
    # Define the pieces, columns, ranks, and special moves
    pieces = ['P', 'N', 'B', 'R', 'Q', 'K', '', 'p', 'n', 'b', 'r', 'q', 'k']
    columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
    special = ['O-O', 'O-O-O', '+', '#', 'x', '=', 'e.p.']

    # Initialize an empty set to store the vocabulary
    vocabulary = set()

    # Generate all possible moves for each piece, column, and rank
    for piece in pieces:
        for col1 in columns:
            for rank1 in ranks:
                for col2 in columns:
                    for rank2 in ranks:
                        # Add moves like "e4", "Nf3", "Bb5+", etc.
                        vocabulary.update([
                            f"{piece}{col1}{rank1}{col2}{rank2}",
                            f"{piece}{col1}{rank1}x{col2}{rank2}",
                            f"{piece}{col2}{rank2}",
                            f"{col2}{rank2}",
                            f"{col2}x{col1}{rank2}",
                            f"{piece}x{col2}{rank2}",
                            f"{piece}{col2}{col1}{rank1}",
                            f"{piece}{rank2}{col2}{rank1}"
                        ])

                        # Add special moves like "O-O", "O-O-O", "Nf3#", etc.
                        for sp in special:
                            vocabulary.update([
                                f"{piece}{col1}{rank1}{col2}{rank2}{sp}",
                                f"{piece}{col1}{rank1}x{col2}{rank2}{sp}",
                                f"{piece}{col2}{rank2}{sp}",
                                f"{col2}{rank2}{sp}",
                                f"{col2}x{col1}{rank2}{sp}",
                                f"{piece}x{col2}{rank2}{sp}",
                                f"{piece}{col2}{col1}{rank1}{sp}",
                                f"{piece}{rank2}{col2}{rank1}{sp}"
                            ])

                # Add simpler moves like "e4", "Nf3", etc.
                vocabulary.add(f"{piece}{col1}{rank1}")

    # Add special moves and annotations
    vocabulary.update(special)

    return list(vocabulary)


def main():
    """
    Main function to create a vocabulary of SAN chess moves and write it to a file.
    """
    # Create the vocabulary
    vocab_list = create_san_vocabulary()

    print(f"Vocabulary length: {len(vocab_list)}")

    # Write the vocabulary to a file
    with open("../data/processed/vocabulary.txt", "w") as f:
        for word in vocab_list:
            f.write(f"{word}\n")

    print("Vocabulary written to file.")


if __name__ == "__main__":
    main()
