import json
import os
import random

import requests as r
from tqdm import tqdm

from Graph import Graph
from secrets import API_KEY, API_URL


class Game:
    GAME_JSON_DIRECTORY = "game_json_files"
    VECTOR_TIMELINE_DIRECTORY = "game_vector_timelines"

    def __init__(self, game_id, experiment):
        self.id = game_id
        self.experiment = experiment
        self.json = {}
        self.graph = Graph(self.id, experiment)
        self.vector_timeline = {}
        self.training_samples = []
        self.vector_relation_method = None
        self.reserved_for_vector_training = False
        self.edge_frequency = {}

        self.json_filename = f'{self.GAME_JSON_DIRECTORY}/{self.id}.json'
        self.vector_timeline_filename = f'{self.VECTOR_TIMELINE_DIRECTORY}/{self.experiment.variables["vector_tag"]}_{self.id}.vtime '

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
        condition_2 = self.json.get("teamfights", None) is not None
        condition_3 = len(self.json.get("teamfights", None)) > 0

        return condition_1 and condition_2 and condition_3

    def get_training_samples(self, vectors):
        self.build_vector_timeline(vectors)
        self.training_samples = []
        number_of_samples = self.experiment.variables['samples_per_game']
        self.build_edge_frequency()

        for i in range(number_of_samples):
            # account for duplicates
            # have a set of picked items, continue picking until it doesn't exist in set
            entity_1, entity_2, timestamp = self.sample_vector_timeline()
            answer = self.if_entities_interact_after_timestamp(entity_1,
                                                               entity_2,
                                                               timestamp)
            sample = entity_1[1] + entity_2[1] + answer

            self.training_samples.append(sample)

        return self.training_samples

    def json_already_exists(self):
        if os.path.isfile(self.json_filename):
            return True

    def vector_timeline_already_exists(self):
        if os.path.isfile(self.vector_timeline_filename):
            return True

    def build_vector_timeline(self, vectors):
        if self.vector_timeline_already_exists():
            with open(self.vector_timeline_filename) as f:
                self.vector_timeline = json.load(f)
            return

        try:
            self.download_json()
        except:
            pass

        self.build_graph()
        self.graph.build_sorted_edges()

        self.vector_timeline[-1] = vectors.vectors

        print("Processing edges...")

        for edge in tqdm(self.graph.sorted_edges):
            self.update_vector_timeline(edge, vectors)
            
        self.fill_empty_spaces_in_vector_timeline()

        with open(self.vector_timeline_filename, 'w') as f:
            json.dump(self.vector_timeline, f)

    def if_entities_interact_after_timestamp(self, entity_1, entity_2, timeslot):
        edges_after_timeslot = []
        for u, v, d in self.graph.graph.edges(data=True):
            if d['timeslot'] > timeslot[0] and u == entity_1[0] and v == entity_2[0]:
                edges_after_timeslot.append((u, v, d['timeslot']))

        if len(edges_after_timeslot) == 0:
            return [0]
        return [1]

    @staticmethod
    def _relate_vectors(vector_1, vector_2):
        resultant_vector = []
        for n1, n2 in zip(vector_1, vector_2):
            resultant_vector.append(n1 + n2)
        return resultant_vector

    def sample_vector_timeline(self):
        random.seed(self.experiment.variables["random_seed"])

        random_timestamp = random.choice(list(self.vector_timeline.keys()))
        vectors_at_random_timestamp = self.vector_timeline[random_timestamp]

        random_entity_1 = random.choice(list(vectors_at_random_timestamp.keys()))
        random_entity_2 = random.choice(list(vectors_at_random_timestamp.keys()))

        while random_entity_1 == random_entity_2:
            random_entity_2 = random.choice(list(vectors_at_random_timestamp.keys()))

        random_entity_vector_1 = vectors_at_random_timestamp[random_entity_1]
        random_entity_vector_2 = vectors_at_random_timestamp[random_entity_2]
        return (random_entity_1, random_entity_vector_1),\
               (random_entity_2, random_entity_vector_2),\
               [0]

    def update_vector_timeline(self, edge, vectors):
        timeslot = edge[2]['timeslot']

        if timeslot not in self.vector_timeline:
            self.vector_timeline[timeslot] = {}

        node_1 = edge[0]
        node_2 = edge[1]

        vector_1 = self.get_latest_vector(node_1, timeslot, vectors)
        vector_2 = self.get_latest_vector(node_2, timeslot, vectors)

        new_node_1_vector = self._relate_vectors(vector_1, vector_2)
        new_node_2_vector = self._relate_vectors(vector_2, vector_1)

        self.vector_timeline[timeslot][node_1] = new_node_1_vector
        self.vector_timeline[timeslot][node_2] = new_node_2_vector

    def get_latest_vector(self, node_name, timeslot, vectors):
        edges_before_timeslot = []

        for u, v, d in self.graph.graph.edges(data=True):
            if d['timeslot'] <= timeslot and u == node_name:
                edges_before_timeslot.append((u, v, d['timeslot']))

        if not edges_before_timeslot:
            return vectors.vectors.get(node_name, [0])

        latest_edge = max(edges_before_timeslot, key=lambda edge: edge[2])
        latest_timeslot = latest_edge[2]

        if self.vector_timeline[latest_timeslot].get(node_name, 0):
            return self.vector_timeline[latest_timeslot][node_name]
        return vectors.vectors.get(node_name, [0])

    def fill_empty_spaces_in_vector_timeline(self):
        timeslots = sorted(self.vector_timeline.items(), key=lambda x: x[0])

        for i in range(1, len(timeslots)):
            previous_timeslot = timeslots[i-1][0]
            current_timeslot = timeslots[i][0]
            values_from_previous_timeslot = self.vector_timeline[previous_timeslot]
            for key, value in values_from_previous_timeslot.items():
                if key not in self.vector_timeline[current_timeslot]:
                    self.vector_timeline[current_timeslot][key] = value

    def build_edge_frequency(self):
        for u, v, d in self.graph.graph.edges(data=True):
            edge = (u, v)
            if edge not in self.edge_frequency:
                self.edge_frequency[edge] = (-5, 0)
            last_seen_timeslot, frequency = self.edge_frequency[edge]
            if d['timeslot'] > last_seen_timeslot:
                d['timeslot'] = last_seen_timeslot
            self.edge_frequency[(u, v)] = (d['timeslot'], frequency+1)
