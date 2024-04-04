import os
import sys
import pandas as pd


# Local
from util import get_games_and_moves_by_username

CURRENT_WORK_DIR = os.getcwd()


def main():
    lichess_username = str(sys.argv[-1]).strip()
    game_list = get_games_and_moves_by_username(lichess_username)
    df = pd.DataFrame(game_list)
    df["white_player"] = df["white_player"].replace("", "ANONYMOUS")
    df["black_player"] = df["black_player"].replace("", "ANONYMOUS")
    df["winning_player"] = df["winning_player"].replace("", "ANONYMOUS")
    df = df.set_index("game_id")

    print("Dataframe head:")
    print(df.head())

    print("\nExporting dataframe to CSV...")
    if CURRENT_WORK_DIR.endswith("scripts"):
        os.chdir("../data/raw")
    else:
        os.chdir("../data/raw")
    df.to_csv(f"games_{lichess_username}.csv")
    print("Export complete.")


if __name__ == "__main__":
    main()
