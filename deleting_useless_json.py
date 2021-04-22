import json
import os

from tqdm import tqdm
from Game import Game


def get_all_game_ids(filename):
    with open(filename, "r") as f:
        json_data = json.load(f)
        game_ids = json_data["match_ids"]
        return game_ids


# ids = get_all_game_ids("game_ids/all.gameid")


json_directory = "game_json_files"


json_filenames = os.listdir(json_directory)
game_ids = [int(name[:-5]) for name in json_filenames]

json_data = {"match_ids": game_ids}

with open("game_ids/all.gameid", "w") as f:
    json.dump(json_data, f)
