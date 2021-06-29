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
        if "results" in self.variables:
            return True
        return False

    def add(self, name, value):
        self.variables[name] = value
        self.save()
        self.load()

    def save(self):
        with open(self.experiment_filename, 'w') as f:
            json.dump(self.variables, f)
