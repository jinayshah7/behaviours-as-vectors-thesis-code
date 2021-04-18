import json
import os


class Experiment:
    EXPERIMENT_DIRECTORY = "experiments"

    def __init__(self, name):
        self.name = name
        self.experiment_filename = f"{self.EXPERIMENT_DIRECTORY}/{self.name}.experiment"
        self.variables = {}
        self.load()

    def load(self):
        if self.experiment_exists():
            with open(self.experiment_filename, 'r') as f:
                self.variables = json.load(f)

    def experiment_exists(self):
        if os.path.isfile(self.experiment_filename):
            return True

    def already_done(self):
        # check if all the relevant files exist
        return False
