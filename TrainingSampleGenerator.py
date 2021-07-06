import json
import os
from multiprocessing import Pool

from tqdm import tqdm

from Game import Game


class TrainingSampleGenerator:
    SAMPLE_DIRECTORY = "classifier_training_samples"

    def __init__(self, experiment, vectors):
        self.experiment = experiment
        self.game_ids_filename = "game_ids/" + experiment.variables["vector_tag"] + "_classifier.gameid"
        self.samples_per_game = self.experiment.variables["samples_per_game"]
        self.samples = []
        self.game_ids = []
        self.games = []
        self.vectors = vectors

        self.things_to_include_from_teamfights = self.experiment.variables["things_to_include_from_teamfights"]
        self.things_to_include_from_player_summary = self.experiment.variables["things_to_include_from_player_summary"]
        self.things_to_include = self.things_to_include_from_player_summary + self.things_to_include_from_teamfights
        self.separate_samples = {}
        self.sample_filenames = {}
        self.generate_sample_filenames()

        for thing in self.things_to_include:
            self.separate_samples[thing] = []

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
        with Pool(32) as p:
            total_samples = p.map(self.collect_samples_from_game, self.game_ids[:5])
        self.combine_samples_from_multiprocess(total_samples)

    def collect_samples_from_game(self, game_id):
        print(f"Sampling from game: {game_id}")
        game = Game(game_id, self.experiment)
        samples_from_this_game = game.get_training_samples(self.vectors, self.things_to_include)
        print(f"Collected samples from game: {game_id}")
        return samples_from_this_game

    def save_samples(self):
        for thing, filename in self.sample_filenames.items():
            with open(filename, 'w') as f:
                json.dump(self.separate_samples[thing], f)
        all_filename = f'{self.SAMPLE_DIRECTORY}/{self.experiment.name}_all_{self.experiment.variables["training_sample_filename"]}'
        with open(all_filename, 'w') as f:
            json.dump(self.samples, f)

    def generate_sample_filenames(self):
        for thing in self.things_to_include:
            filename = f'{self.SAMPLE_DIRECTORY}/{self.experiment.name}_{thing}_{self.experiment.variables["training_sample_filename"]}'
            self.sample_filenames[thing] = filename

    def combine_samples_from_multiprocess(self, total_samples):
        for dict_of_samples in total_samples:
            for category, samples in dict_of_samples.items():
                self.samples.extend(samples)
                self.separate_samples[category].extend(samples)
        self.separate_samples["all"] = self.samples
