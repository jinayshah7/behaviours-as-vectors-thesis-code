import json
import os

import networkx as nx
from tqdm import tqdm

from Game import Game


class VectorTrainingSampleGenerator:
    VECTOR_TRAINING_DIRECTORY = "vector_training_samples"
    GAME_ID_FOLDER = "game_ids/"

    def __init__(self, experiment):
        self.experiment = experiment
        self.game_ids_filename = self.GAME_ID_FOLDER + self.experiment.variables["vector_tag"] + "_vector.gameid"

        self.node2vec_training_edges_filename = self.experiment.variables["node2vec_training_edges_filename"]
        self.node2vec_training_edges_filename = f"{self.VECTOR_TRAINING_DIRECTORY}/{self.experiment.name}_{self.node2vec_training_edges_filename}"

        self.line_training_edges_filename = self.experiment.variables["line_training_edges_filename"]
        self.line_training_edges_filename = f"{self.VECTOR_TRAINING_DIRECTORY}/{self.experiment.name}_{self.line_training_edges_filename}"

        self.tgn_training_edges_filename = self.experiment.variables["tgn_training_edges_filename"]
        self.tgn_training_edges_filename = f"{self.VECTOR_TRAINING_DIRECTORY}/{self.experiment.name}_{self.tgn_training_edges_filename}"

        self.name_id_mapping_filename = self.experiment.variables["edge_names_filename"]
        self.name_id_mapping_filename = f"{self.VECTOR_TRAINING_DIRECTORY}/{self.experiment.name}_{self.name_id_mapping_filename}"

        self.samples = []
        self.game_ids = []
        self.edge_list = []
        self.name_id_mapping = {}
        self.graph = nx.MultiGraph()

    def load_game_ids(self):
        if self.game_id_file_exists():
            with open(self.game_ids_filename, 'r') as f:
                self.game_ids = json.load(f)
                self.game_ids = self.game_ids["match_ids"]

    def game_id_file_exists(self):
        if os.path.isfile(self.game_ids_filename):
            return True

    def generate_big_graph(self):
        self.load_game_ids()
        for game_id in tqdm(self.game_ids[:]):
            game = Game(game_id, self.experiment)
            game.download_json()
            game.build_graph()
            self.graph.add_edges_from(game.graph.graph.edges)

    def build_edge_list(self):
        for single_edge in self.graph.edges:
            source, destination, timestamp = single_edge
            self.edge_list.append((source, destination, timestamp))
        self.build_name_id_mapping()
        self.update_edge_list_with_ids()

    def update_edge_list_with_ids(self):
        new_edge_list = []

        for single_edge in self.graph.edges:
            source, destination, timestamp = single_edge

            source_id = self.name_id_mapping[source]
            destination_id = self.name_id_mapping[destination]

            new_edge_list.append((source_id, destination_id, timestamp))

        self.edge_list = new_edge_list

    def build_name_id_mapping(self):
        sources = list(set([edge[0] for edge in self.edge_list]))
        destinations = list(set([edge[1] for edge in self.edge_list]))

        all_entities = sources + destinations

        for entity_number, entity_name in enumerate(all_entities):
            self.name_id_mapping[entity_name] = entity_number

    def save_edges_for_tgn(self):
        with open(self.tgn_training_edges_filename, 'w') as f:
            for single_edge in sorted(self.edge_list, key=lambda x: x[2]):
                f.write(f"{single_edge[0]},{single_edge[1]},{single_edge[2]}\n")

    def save_edges_for_node2vec(self):
        with open(self.node2vec_training_edges_filename, 'w') as f:
            edges = [(edge[0], edge[1]) for edge in self.edge_list]
            edges = list(set(edges))
            for single_edge in edges:
                f.write(f"{single_edge[0]} {single_edge[1]}\n")

    def save_edges_for_line(self):
        with open(self.line_training_edges_filename, 'w') as f:
            edges = [(edge[0], edge[1]) for edge in self.edge_list]
            edges = list(set(edges))
            added_edges = set()
            for single_edge in edges:
                if (single_edge[0], single_edge[1]) in added_edges:
                    continue
                if single_edge[0] == single_edge[1]:
                    continue
                f.write(f"{single_edge[0]} {single_edge[1]}\n")
                f.write(f"{single_edge[1]} {single_edge[0]}\n")
                added_edges.add((single_edge[0], single_edge[1]))
                added_edges.add((single_edge[1], single_edge[0]))

    def save_edge_list(self):
        new_reverse_mapping = {}
        for key, value in self.name_id_mapping.items():
            new_reverse_mapping[value] = key

        with open(self.name_id_mapping_filename, 'w') as f:
            json.dump(new_reverse_mapping, f)
