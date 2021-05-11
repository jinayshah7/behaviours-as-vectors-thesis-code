import json

from numpy import array
from sklearn.linear_model import LogisticRegression


class ClassifierTrainer:
    SAMPLE_DIRECTORY = "classifier_training_samples"

    def __init__(self, experiment):
        self.experiment = experiment
        self.vectors = None
        self.target_variable = None
        self.loaded_samples = None
        self.vector_size = 0
        self.sample_filename = f'{self.SAMPLE_DIRECTORY}/{self.experiment.name}_{self.experiment.variables["training_sample_filename"]}'

    def generate_result(self):
        self.load_samples()
        self.format_samples()
        # replace this random state = 0 with seed from experiment
        # put some hyper-parameter tuning code here
        clf = LogisticRegression(random_state=0).fit(self.vectors,
                                                     self.target_variable)
        clf.score(self.vectors,
                  self.target_variable)
        # add code to save results in a json file

    def load_samples(self):
        with open(self.sample_filename) as f:
            rows = json.load(f)

        number_of_rows = len(rows[0])
        self.vector_size = int((number_of_rows - 1) / 2)

        self.target_variable = array([row[-1] for row in rows])
        self.vectors = array([row[:-1] for row in rows])

    def format_samples(self):
        pass
