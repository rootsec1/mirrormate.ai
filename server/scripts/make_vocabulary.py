def create_san_vocabulary():
    pieces = ['P', 'N', 'B', 'R', 'Q', 'K', '', 'p', 'n', 'b', 'r', 'q', 'k']
    columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
    special = ['O-O', 'O-O-O', '+', '#', 'x', '=', 'e.p.']

    vocabulary = set()
    for piece in pieces:
        for col1 in columns:
            for rank1 in ranks:
                for col2 in columns:
                    for rank2 in ranks:
                        # Add moves like "e4", "Nf3", "Bb5+", etc.
                        line1 = f"{piece}{col1}{rank1}{col2}{rank2}"
                        line2 = f"{piece}{col1}{rank1}x{col2}{rank2}"
                        line3 = f"{piece}{col2}{rank2}"
                        line4 = f"{col2}{rank2}"
                        line5 = f"{col2}x{col1}{rank2}"
                        line6 = f"{piece}x{col2}{rank2}"
                        line7 = f"{piece}{col2}{col1}{rank1}"
                        line8 = f"{piece}{rank2}{col2}{rank1}"

                        vocabulary.add(line1)
                        vocabulary.add(line2)
                        vocabulary.add(line3)
                        vocabulary.add(line4)
                        vocabulary.add(line5)
                        vocabulary.add(line6)
                        vocabulary.add(line7)
                        vocabulary.add(line8)

                        for sp in special:
                            # Add moves like "O-O", "O-O-O", "Nf3#", etc.
                            line9 = f"{line1}{sp}"
                            line10 = f"{line2}{sp}"
                            line11 = f"{line3}{sp}"
                            line12 = f"{line4}{sp}"
                            line13 = f"{line5}{sp}"
                            line14 = f"{line6}{sp}"
                            line15 = f"{line7}{sp}"
                            line16 = f"{line8}{sp}"

                            vocabulary.add(line8)
                            vocabulary.add(line9)
                            vocabulary.add(line10)
                            vocabulary.add(line11)
                            vocabulary.add(line12)
                            vocabulary.add(line13)
                            vocabulary.add(line14)
                            vocabulary.add(line15)
                            vocabulary.add(line16)

                # Add simpler moves like "e4", "Nf3", etc.
                vocabulary.add(f"{piece}{col1}{rank1}")
    # Add special moves and annotations
    vocabulary.update(special)
    return list(vocabulary)


def main():
    vocab_list = create_san_vocabulary()
    print(f"Vocabulary length: {len(vocab_list)}")
    # vocab: key=word, value=index
    # reverse_vocab: key=index, value=word
    with open("../data/processed/vocabulary.txt", "w") as f:
        for word in vocab_list:
            f.write(f"{word}\n")
    print("Vocabulary written to file.")


if __name__ == "__main__":
    main()
