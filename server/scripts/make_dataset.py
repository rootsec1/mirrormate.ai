import os
import sys
import pandas as pd

# Local import
from util import get_games_and_moves_by_username

# Get the current working directory
CURRENT_WORK_DIR = os.getcwd()


def main():
    """
    Main function to fetch games and moves by a specific user from Lichess, 
    process the data, and save it as a CSV file.
    """
    # Get the Lichess username from the command line arguments
    lichess_username = str(sys.argv[-1]).strip()

    # Fetch the games and moves by the specified user
    game_list = get_games_and_moves_by_username(lichess_username)

    # Convert the list of games into a DataFrame
    df = pd.DataFrame(game_list)

    # Replace missing player names with "ANONYMOUS"
    df["white_player"] = df["white_player"].replace("", "ANONYMOUS")
    df["black_player"] = df["black_player"].replace("", "ANONYMOUS")
    df["winning_player"] = df["winning_player"].replace("", "ANONYMOUS")

    # Set the game ID as the index of the DataFrame
    df = df.set_index("game_id")

    # Print the first few rows of the DataFrame
    print("Dataframe head:")
    print(df.head())

    # Export the DataFrame to a CSV file
    print("\nExporting dataframe to CSV...")
    # Change the current working directory to the raw data directory
    if CURRENT_WORK_DIR.endswith("scripts"):
        os.chdir("../data/raw")
    else:
        os.chdir("../data/raw")
    # Save the DataFrame as a CSV file
    df.to_csv(f"games_{lichess_username}.csv")
    print("Export complete.")


# Run the main function if this script is run as the main module
if __name__ == "__main__":
    main()
