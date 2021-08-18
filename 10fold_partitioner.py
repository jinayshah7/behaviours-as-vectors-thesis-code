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


def get_start_end_indexes(experiment_name, total_games):
    chunks = experiment_name.split('-')
    fold_number = (int(chunks[-1]) - 1)
    start_index = (fold_number * 10) * total_games
    end_index = ((fold_number * 10) + 10) * total_games
    return start_index, end_index


def main():
    for experiment_name in LIST_OF_EXPERIMENTS:
        experiment = Experiment(experiment_name)

        game_ids = get_all_game_ids(ALL_GAME_IDS_FILE)

        random_seed = experiment.variables["random_seed_1"]
        random.seed(random_seed)
        random.shuffle(game_ids)

        total_games = len(game_ids)
        experiment_name = experiment.variables["vector_tag"]
        classifier_start_index, classifier_end_index = get_start_end_indexes(experiment_name, total_games)

        vector_ids = game_ids[0:classifier_start_index] + game_ids[classifier_end_index:]
        classifier_ids = game_ids[classifier_start_index:classifier_end_index]

        classifier_game_ids_filename = GAME_ID_FOLDER + experiment.variables["vector_tag"] + "_classifier.gameid"

        vector_game_ids_filename = GAME_ID_FOLDER + experiment.variables["vector_tag"] + "_vector.gameid"

        save_game_ids(classifier_ids, classifier_game_ids_filename)
        save_game_ids(vector_ids, vector_game_ids_filename)


if __name__ == '__main__':
    main()
