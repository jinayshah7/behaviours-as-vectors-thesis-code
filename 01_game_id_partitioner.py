import json
import random
from list_of_experiments import LIST_OF_EXPERIMENTS
from Experiment import Experiment

ALL_GAME_IDS_FILE = "game_ids/all.gameid"
GAME_ID_FOLDER = "game_ids/"


def get_all_game_ids(filename):
    with open(filename, "r") as f:
        json_data = json.load(f)
        game_ids = json_data["match_ids"]
        return game_ids


def save_game_ids(game_ids, filename):
    ids = {"match_ids": game_ids}

    with open(filename, "w") as f:
        json.dump(ids, f)


def main():
    for experiment_name in LIST_OF_EXPERIMENTS:
        experiment = Experiment(experiment_name)

        if experiment.already_done():
            continue

        number_of_games = experiment.variables["number_of_games"]
        game_ids = get_all_game_ids(ALL_GAME_IDS_FILE)
        game_ids = game_ids[:number_of_games]

        random_seed = experiment.variables["random_seed_1"]
        random.seed(random_seed)
        random.shuffle(game_ids)

        percent_to_reserve_for_vectors = experiment.variables["percentage_to_reserve_for_vectors"]

        amount_to_reserve_for_vectors = int(percent_to_reserve_for_vectors * len(game_ids))

        vector_ids = game_ids[:amount_to_reserve_for_vectors]
        classifier_ids = game_ids[amount_to_reserve_for_vectors:]

        classifier_game_ids_filename = GAME_ID_FOLDER + experiment.variables["vector_tag"] + "_classifier.gameid"

        vector_game_ids_filename = GAME_ID_FOLDER + experiment.variables["vector_tag"] + "_vector.gameid"

        save_game_ids(classifier_ids, classifier_game_ids_filename)
        save_game_ids(vector_ids, vector_game_ids_filename)


if __name__ == '__main__':
    main()
