import json
from statistics import mean

from numpy import array
from numpy.core import std
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import make_pipeline


class ClassifierTrainer:
    SAMPLE_DIRECTORY = "classifier_training_samples"

    def __init__(self, experiment):
        self.experiment = experiment
        self.vectors = {}
        self.target_variable = {}
        self.loaded_samples = None
        self.vector_size = 0
        self.results = {}

        self.things_to_include_from_teamfights = self.experiment.variables["things_to_include_from_teamfights"]
        self.things_to_include_from_player_summary = self.experiment.variables["things_to_include_from_player_summary"]
        self.things_to_include = self.things_to_include_from_player_summary + self.things_to_include_from_teamfights
        self.things_to_include.append("all")

    def generate_result(self):
        random_seed = self.experiment.variables["random_seed_2"]
        print(f"Experiment: {self.experiment.variables['vector_tag']}")
        for thing in self.things_to_include:
            clf = make_pipeline(preprocessing.StandardScaler(),
                                LogisticRegression(random_state=random_seed))
            cv = KFold(n_splits=10)

            scores = cross_val_score(clf,
                                     self.vectors[thing],
                                     self.target_variable[thing],
                                     scoring='accuracy',
                                     cv=cv)

            print(f'{thing} test score: %.3f (%.3f)' % (mean(scores), std(scores)))
            self.results[f"{thing}_test_scores"] = list(scores)
            self.save_result()

    def load_samples(self, sample_generator):
        for thing, rows in sample_generator.separate_samples.items():

            number_of_rows = len(rows[0])
            self.vector_size = int((number_of_rows - 1) / 2)

            vectors = []
            target_variables = []
            for row in rows:
                if (len(row) - 1) != (2 * self.vector_size):
                    continue
                vectors.append(row[:-1])
                target_variables.append(row[-1])
            self.target_variable[thing] = array(target_variables)
            self.vectors[thing] = array(vectors)

    def save_result(self):
        self.experiment.add("results", self.results)
