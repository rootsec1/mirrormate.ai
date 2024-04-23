import sys
import os
import pandas as pd
from tqdm import tqdm
from util import explode_game_into_moves, preprocess_lichess_export_data

# Get the current working directory
CURRENT_WORK_DIR = os.getcwd()


def main():
    """
    Main function to preprocess Lichess export data, explode the games into moves,
    and save the result as a CSV file.
    """
    # Get the Lichess username from the command line arguments
    lichess_username = str(sys.argv[-1]).strip()

    # Preprocess the Lichess export data
    game_list = preprocess_lichess_export_data(lichess_username)

    exploded_game_list = []
    # Loop through each game
    for game in tqdm(game_list):
        # Explode the game into moves and add them to the list
        exploded_game_list.extend(
            explode_game_into_moves(game, lichess_username)
        )

    # Convert the list of exploded games into a DataFrame
    exploded_game_df = pd.DataFrame(
        exploded_game_list,
        columns=["game_id", "input_sequence", "target_move"]
    )

    print("Exporting dataframe to CSV...")
    # Change the current working directory to the processed data directory
    if CURRENT_WORK_DIR.endswith("scripts"):
        os.chdir("../data/processed")
    else:
        os.chdir("../data/processed")
    # Save the DataFrame as a CSV file
    exploded_game_df.to_csv(
        f"sequence_target_map_{lichess_username}.csv",
        index=False
    )
    print("Export complete.")


# Run the main function if this script is run as the main module
if __name__ == "__main__":
    main()
