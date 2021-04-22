import json
import os

from Game import Game


class TrainingSampleGenerator:
    SAMPLE_DIRECTORY = "classifier_training_samples"

    def __init__(self, experiment, vectors):
        self.experiment = experiment
        self.game_ids_filename = self.experiment.variables["game_ids_filename"]
        self.samples_per_game = self.experiment.variables["samples_per_game"]
        self.samples = []
        self.game_ids = []
        self.games = []
        self.vectors = vectors

    def load_game_ids(self):
        if self.game_id_file_exists():
            with open(self.game_ids_filename, 'r') as f:
                self.game_ids = json.load(f)
                self.game_ids = self.game_ids["match_ids"]

    def game_id_file_exists(self):
        if os.path.isfile(self.game_ids_filename):
            return True

    def generate_samples(self):
        self.load_game_ids()
        for game_id in self.game_ids:
            game = Game(game_id)
            samples_from_this_game = game.get_training_samples(self.samples_per_game,
                                                               self.vectors)
            self.games.append(game)
            self.samples.extend(samples_from_this_game)

    def save_samples(self):
        # save in npy format
        pass

    def samples_already_present(self):
        # load them if present
        pass
