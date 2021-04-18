import json
import os
import requests as r
from secrets import API_KEY, API_URL
import numpy as np


class Game:
    GRAPH_DIRECTORY = "game_graph_files"
    GAME_JSON_DIRECTORY = "game_json_files"
    VECTOR_TIMELINE_DIRECTORY = "game_vector_timelines"

    def __init__(self, game_id):
        self.id = game_id
        self.json = {}
        self.graph = {}
        self.vector_timeline = {}
        self.training_samples = []
        self.vector_relation_method = None
        self.reserved_for_vector_training = False
        self.this_works = False

        self.json_filename = f'{self.GAME_JSON_DIRECTORY}/{self.id}.json'
        self.graph_filename = f'{self.GRAPH_DIRECTORY}/{self.id}.graph'
        self.vector_timeline_filename = f'{self.VECTOR_TIMELINE_DIRECTORY}/{self.id}.vtime'

        self.url = f"{API_URL}/matches/{self.id}?api_key={API_KEY}"

    def build_graph(self):
        if self.graph_already_exists():
            # load the graph in memory
            return
        self.build_timestamps()

        for player in self.json["teamfights"]:
            pass

        for player in self.json["players"]:
            pass

        # build the networkx graph
        # also save the graph after building it
        pass

    def download_json(self):
        if self.json_already_exists():
            with open(self.json_filename, 'r') as f:
                self.json = json.load(f)
            return

        self.json = r.get(self.url).json()

        if "teamfights" in self.json and self.json["teamfights"] is not None:
            with open(self.json_filename, 'w') as f:
                json.dump(self.json, f)
                self.this_works = True

    def get_training_samples(self, number_of_samples, vectors):
        for i in range(number_of_samples):
            entity_1, entity_2, timestamp = self.sample_vector_timeline()
            answer = self.if_entities_interact_after_timestamp(entity_1, entity_2, timestamp)
            sample = np.concatenate((entity_1, entity_2, timestamp, answer))
            self.training_samples.append(sample)

        return self.training_samples

    def json_already_exists(self):
        if os.path.isfile(self.json_filename):
            return True

    def graph_already_exists(self):
        if os.path.isfile(self.graph_filename):
            return True

    def vector_timeline_already_exists(self):
        if os.path.isfile(self.vector_timeline_filename):
            return True

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

    def if_entities_interact_after_timestamp(self, entity_1, entity_2, timestamp):
        # get all interactions after this timestamp
        # see if entity_! and entity_2 are present in this
        return np.array([1])

    @staticmethod
    def _relate_vectors(vector_1, vector_2):
        return np.add(vector_1, vector_2)

    def build_timestamps(self):
        # get the ranges from teamfights
        # make a dictionary of them
        pass

    def sample_vector_timeline(self):
        x = self.vector_timeline
        vector_1 = np.array([0,0])
        vector_2 = np.array([0, 0])
        return vector_1, vector_2, np.array([0])
