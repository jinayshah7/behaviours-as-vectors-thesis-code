import json
import os
import requests as r

from Graph import Graph
from secrets import API_KEY, API_URL


class Game:

    GAME_JSON_DIRECTORY = "game_json_files"
    VECTOR_TIMELINE_DIRECTORY = "game_vector_timelines"

    def __init__(self, game_id):
        self.id = game_id
        self.json = {}
        self.graph = Graph(self.id)
        self.vector_timeline = {}
        self.training_samples = []
        self.vector_relation_method = None
        self.reserved_for_vector_training = False

        self.json_filename = f'{self.GAME_JSON_DIRECTORY}/{self.id}.json'
        self.vector_timeline_filename = f'{self.VECTOR_TIMELINE_DIRECTORY}/{self.id}.vtime'

        self.url = f"{API_URL}/matches/{self.id}?api_key={API_KEY}"

    def build_graph(self):
        if self.json_is_valid():
            self.graph.build(self.json)

    def download_json(self):
        if self.json_already_exists():
            with open(self.json_filename, 'r') as f:
                self.json = json.load(f)
            return

        self.json = r.get(self.url).json()

        if self.json_is_valid():
            with open(self.json_filename, 'w') as f:
                json.dump(self.json, f)

    def json_is_valid(self):
        condition_1 = "teamfights" in self.json
        condition_2 = self.json["teamfights"] is not None

        return condition_1 and condition_2

    def get_training_samples(self, number_of_samples, vectors):
        self.build_vector_timeline(vectors)
        self.training_samples = []

        for i in range(number_of_samples):
            entity_1, entity_2, timestamp = self.sample_vector_timeline()
            answer = self.if_entities_interact_after_timestamp(entity_1,
                                                               entity_2,
                                                               timestamp)
            sample = entity_1 + entity_2 + timestamp + answer

            self.training_samples.append(sample)

        return self.training_samples

    def json_already_exists(self):
        if os.path.isfile(self.json_filename):
            return True

    def vector_timeline_already_exists(self):
        if os.path.isfile(self.vector_timeline_filename):
            return True

    # TODO
    def build_vector_timeline(self, vectors):
        if self.vector_timeline_already_exists():
            # load the file
            return

        self.download_json()
        self.build_graph()

        # sort the interactions based on timeline
        # for each interaction,
        # build a new copy of the vectors
        # update the vectors based on the interaction.
        pass

    # TODO
    def if_entities_interact_after_timestamp(self, entity_1, entity_2, timestamp):
        # get all interactions after this timestamp
        # see if entity_! and entity_2 are present in this
        return [1]

    @staticmethod
    def _relate_vectors(vector_1, vector_2):
        resultant_vector = []
        for n1, n2 in zip(vector_1, vector_2):
            resultant_vector.append(n1 + n2)
        return resultant_vector

    # TODO
    def sample_vector_timeline(self):
        x = self.vector_timeline
        vector_1 = [0, 0]
        vector_2 = [0, 0]
        return vector_1, vector_2, [0]
