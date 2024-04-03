import sys
import os
import pandas as pd

from tqdm import tqdm

from util import explode_game_into_moves, preprocess_lichess_export_data


CURRENT_WORK_DIR = os.getcwd()


def main():
    lichess_username = str(sys.argv[-1]).strip()
    game_list = preprocess_lichess_export_data(lichess_username)

    exploded_game_list = []
    for game in tqdm(game_list):
        exploded_game_list.extend(
            explode_game_into_moves(game, lichess_username)
        )

    # Convert explode_game_into_moves to a dataframe
    exploded_game_df = pd.DataFrame(
        exploded_game_list,
        columns=["game_id", "input_sequence", "target_move"]
    )

    print("Exporting dataframe to CSV...")
    if CURRENT_WORK_DIR.endswith("scripts"):
        os.chdir("../data/processed")
    else:
        os.chdir("../data/processed")
    exploded_game_df.to_csv(
        f"sequence_target_map_{lichess_username}.csv",
        index=False
    )
    print("Export complete.")


if __name__ == "__main__":
    main()
