import json
import os
import numpy as np


class Vectors:
    VECTOR_DIRECTORY = "initial_vectors"
    ID_TO_NAME_FILENAME = f"{VECTOR_DIRECTORY}/entity_id_names.json"

    def __init__(self, experiment):
        self.experiment = experiment
        self.vectors = {}
        self.tag = self.experiment.variables["vector_tag"]
        self.vector_filename = f"{self.VECTOR_DIRECTORY}/{self.tag}.vector"
        self.load()
        self.error = 0
        self.entity_id_name_table = {}

    def load(self):
        if self.vectors_not_present():
            self.error = -1
            return

        with open(self.vector_filename) as f:
            vectors_from_file = f.read().split('\n')
        vectors_from_file = [line for line in vectors_from_file if line != '']
        self.build_entity_id_name_table()

        for vector in vectors_from_file:
            entity_name, vector = self.process_vector_from_file(vector)
            self.vectors[entity_name] = vector

    def vectors_not_present(self):
        if not os.path.isfile(self.vector_filename):
            return True

    def process_vector_from_file(self, vector):
        numbers = [int(number) for number in vector.split(',')]
        entity_id = str(numbers[0])
        name = self.entity_id_name_table[entity_id]
        vector = np.array(numbers[1:])
        return name, vector

    def build_entity_id_name_table(self):
        with open(self.ID_TO_NAME_FILENAME) as f:
            self.entity_id_name_table = json.load(f)
