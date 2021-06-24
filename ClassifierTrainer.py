import json
import numpy as np
from numpy import array
from sklearn.linear_model import LogisticRegression


class ClassifierTrainer:
    SAMPLE_DIRECTORY = "classifier_training_samples"

    def __init__(self, experiment):
        self.experiment = experiment
        self.vectors = {

        }
        self.target_variable = {

        }
        self.loaded_samples = None
        self.vector_size = 0

        self.things_to_include_from_teamfights = self.experiment.variables["things_to_include_from_teamfights"]
        self.things_to_include_from_player_summary = self.experiment.variables["things_to_include_from_player_summary"]
        self.things_to_include = self.things_to_include_from_player_summary + self.things_to_include_from_teamfights
        self.things_to_include.append("all")

        self.sample_filenames = {}
        for thing in self.things_to_include:
            filename = f'{self.SAMPLE_DIRECTORY}/{self.experiment.name}_{thing}_{self.experiment.variables["training_sample_filename"]}'
            self.sample_filenames[thing] = filename

    def generate_result(self):
        self.load_samples()
        random_seed = self.experiment.variables["random_seed_2"]
        print(f"Experiment: ")
        for thing in self.things_to_include:
            ninety_percent = int(len(self.vectors[thing]) * 0.9)

            clf = LogisticRegression(random_state=random_seed).fit(self.vectors[thing][:ninety_percent],
                                                                   self.target_variable[thing][:ninety_percent])
            print(thing, ": ", clf.score(self.vectors[thing][ninety_percent:],
                                         self.target_variable[thing][ninety_percent:]))
            self.save_samples()

    def load_samples(self):
        for thing, filename in self.sample_filenames.items():
            with open(filename) as f:
                rows = json.load(f)

            number_of_rows = len(rows[0])
            self.vector_size = int((number_of_rows - 1) / 2)

            vectors = []
            target_variables = []
            for row in rows:
                if (len(row) - 1) != (2*self.vector_size):
                    continue
                vectors.append(row[:-1])
                target_variables.append(row[-1])
            # self.target_variable[thing] = array([row[-1] for row in rows])
            # self.vectors[thing] = [row[:-1] for row in rows]
            self.target_variable[thing] = array(target_variables)
            self.vectors[thing] = array(vectors)

    def save_samples(self):
        pass
