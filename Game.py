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
        self.edge_frequency_category_wise = {}

        self.json_filename = f'{self.GAME_JSON_DIRECTORY}/{self.id}.json'
        self.vector_timeline_filename = f'{self.VECTOR_TIMELINE_DIRECTORY}/{self.experiment.variables["vector_tag"]}_{self.id}.vtime '

        self.url = f"{API_URL}/matches/{self.id}?api_key={API_KEY}"

    def build_graph(self):
        if self.json_is_valid():
            self.graph.build(self.json)

    def download_json(self):
        try:
            if self.json_already_exists():
                with open(self.json_filename, 'r') as f:
                    self.json = json.load(f)
                return
        except Exception as e:
            self.json = r.get(self.url).json()

            if self.json_is_valid():
                with open(self.json_filename, 'w') as f:
                    json.dump(self.json, f)

    def json_is_valid(self):
        condition_1 = "teamfights" in self.json
        if self.json.get("teamfights", None) is None:
            return False
        condition_3 = len(self.json.get("teamfights", [])) > 0

        return condition_1 and condition_3

    def get_training_samples(self, vectors, categories_to_include):
        self.build_vector_timeline(vectors)
        self.training_samples = {}
        self.build_edge_frequency()

        number_of_samples = self.experiment.variables['samples_per_game']
        random.seed(self.experiment.variables["random_seed_2"])

        for category in categories_to_include:
            self.training_samples[category] = self.generate_samples_for_category(category, number_of_samples)

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
                try:
                    self.download_json()
                except:
                    pass
                self.build_graph()
                self.graph.build_sorted_edges()
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

    @staticmethod
    def _relate_vectors(vector_1, vector_2):
        resultant_vector = []
        for n1, n2 in zip(vector_1, vector_2):
            resultant_vector.append(n1 + n2)
        return resultant_vector

    def sample_vector_timeline(self, specific_category):
        
        random_entity_1, random_entity_2 = self.get_two_random_entities(specific_category)

        last_seen, count, category = self.edge_frequency[(random_entity_1, random_entity_2)]
        random_timestamp, answer = self.find_timestamp(last_seen)

        random_entity_vector_1 = self.vector_timeline[random_timestamp][random_entity_1]
        random_entity_vector_2 = self.vector_timeline[random_timestamp][random_entity_2]

        return (random_entity_1, random_entity_vector_1), \
               (random_entity_2, random_entity_vector_2), \
               [answer]

    def update_vector_timeline(self, edge, vectors):
        timeslot = int(edge[2])

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
            if d.get('timeslot', -1) <= timeslot and u == node_name:
                edges_before_timeslot.append((u, v, d.get('timeslot', -1)))

        if not edges_before_timeslot:
            return vectors.vectors.get(node_name, [0, 0, 0])

        latest_edge = max(edges_before_timeslot, key=lambda edge: edge[2])
        latest_timeslot = latest_edge[2]

        if self.vector_timeline[latest_timeslot].get(node_name, 0):
            return self.vector_timeline[latest_timeslot][node_name]
        return vectors.vectors.get(node_name, [0, 0, 0])

    def fill_empty_spaces_in_vector_timeline(self):
        timeslots = sorted(self.vector_timeline.items(), key=lambda x: int(x[0]))

        for i in range(1, len(timeslots)):
            previous_timeslot = timeslots[i - 1][0]
            current_timeslot = timeslots[i][0]
            values_from_previous_timeslot = self.vector_timeline[previous_timeslot]
            for key, value in values_from_previous_timeslot.items():
                if key not in self.vector_timeline[current_timeslot]:
                    self.vector_timeline[current_timeslot][key] = value

    def build_edge_frequency(self):
        for node_1, node_2, timeslot, category in self.graph.sorted_edges:
            edge = (node_1, node_2)
            if edge not in self.edge_frequency:
                self.edge_frequency[edge] = (-1, 0, category)
            last_seen_timeslot, frequency, category = self.edge_frequency[edge]
            if timeslot < last_seen_timeslot:
                timeslot = last_seen_timeslot
            self.edge_frequency[(node_1, node_2)] = (timeslot, frequency + 1, category)

        for key, value in self.edge_frequency.items():
            node_1, node_2 = key
            timeslot, frequency, category = value
            if category not in self.edge_frequency_category_wise:
                self.edge_frequency_category_wise[category] = {}
            self.edge_frequency_category_wise[category][(node_1, node_2)] = (timeslot, frequency)

    def find_timestamp(self, last_seen):
        all_timestamps_string = list(self.vector_timeline.keys())
        all_timestamps = [int(t) for t in all_timestamps_string]
        all_timestamps = sorted(all_timestamps)
        entities_interact = random.choice([0, 1])
        index_of_last_seen = all_timestamps.index(last_seen)

        timestamps_before = all_timestamps[:index_of_last_seen]
        timestamps_after = all_timestamps[index_of_last_seen:]

        timestamps_to_sample = timestamps_before
        if not entities_interact:
            timestamps_to_sample = timestamps_after

        if len(timestamps_to_sample) == 0:
            if len(timestamps_before) == 0:
                timestamps_to_sample = timestamps_after
                entities_interact = 0
            if len(timestamps_after) == 0:
                timestamps_to_sample = timestamps_before
                entities_interact = 1

        random_sampled_timestamp = random.choice(timestamps_to_sample)
        return random_sampled_timestamp, entities_interact

    def get_two_random_entities(self, specific_category):
        interactions_to_choose_from = list(self.edge_frequency_category_wise[specific_category].keys())
        random_entity_1, random_entity_2 = random.choice(interactions_to_choose_from)
        return random_entity_1, random_entity_2

    def generate_samples_for_category(self, category, number_of_samples):
        samples = []
        for i in range(number_of_samples):
            try:
                entity_1, entity_2, answer = self.sample_vector_timeline(category)
            except Exception as e:
                continue
            sample = entity_1[1] + entity_2[1] + answer
            samples.append(sample)

        return samples
