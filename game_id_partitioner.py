import json
from tqdm import tqdm
from Game import Game

ALL_GAME_IDS_FILE = "game_ids/all.gameid"
IDS_RESERVED_FOR_VECTORS_FILENAME = "game_ids/vector.gameid"
IDS_RESERVED_FOR_CLASSIFIER_FILENAME = "game_ids/classifier.gameid"

PERCENT_TO_RESERVE_FOR_VECTORS = 0.7


def get_all_game_ids(filename):
    with open(filename, "r") as f:
        json_data = json.load(f)
        game_ids = json_data["match_ids"]
        return game_ids


def get_hero_frequency(games):
    hero_frequency = {}
    for game in tqdm(games):
        game.download_json()
        hero_ids = [player["hero_id"] for player in game.json["players"]]
        for hero_id in hero_ids:
            if hero_id not in hero_frequency:
                hero_frequency[hero_id] = 0
            hero_frequency[hero_id] += 1
    return hero_frequency


def save_game_ids(game_ids, filename):
    ids = {"match_ids": game_ids}

    with open(filename, "w") as f:
        json.dump(ids, f)


def main():
    game_ids = get_all_game_ids(ALL_GAME_IDS_FILE)
    game_ids.sort()

    amount_to_reserve_for_vectors = int(PERCENT_TO_RESERVE_FOR_VECTORS * len(game_ids))

    vector_ids = game_ids[:amount_to_reserve_for_vectors]
    classifier_ids = game_ids[amount_to_reserve_for_vectors:]

    save_game_ids(vector_ids, IDS_RESERVED_FOR_VECTORS_FILENAME)
    save_game_ids(classifier_ids, IDS_RESERVED_FOR_CLASSIFIER_FILENAME)


if __name__ == '__main__':
    main()
