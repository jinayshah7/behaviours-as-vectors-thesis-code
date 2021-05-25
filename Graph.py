import json
import os
import networkx as nx


class Graph:
    GRAPH_DIRECTORY = "game_graph_files"

    def __init__(self, game_id, experiment):
        self.id = game_id
        self.experiment = experiment
        self.graph = nx.MultiGraph()
        self.graph_filename = f'{self.GRAPH_DIRECTORY}/{self.id}.graph'
        self.timeslots = []
        self.json = {}
        self.player_number_to_hero_id = {}
        self.sorted_edges = None
        # self.build()

    def build(self, json_data):
        self.json = json_data
        if self.already_exists():
            self.load_graph_from_file()

        self.build_timeslots()
        self.get_hero_ids()
        self.parse_player_summary()
        self.parse_teamfights()
        self.save_graph()

    def load_graph_from_file(self):
        with open(self.graph_filename) as f:
            edges = json.load(f)
            self.graph.add_edges_from(edges)

    def already_exists(self):
        if os.path.isfile(self.graph_filename):
            return True

    def build_timeslots(self):
        for teamfight in self.json["teamfights"]:
            self.timeslots.append(teamfight["start"])
            self.timeslots.append(teamfight["end"])
        self.timeslots.sort()

    def parse_teamfights(self):
        for teamfight in self.json["teamfights"]:
            timeslot = self.get_timeslot(int(teamfight["start"]))

            for player_number, player in enumerate(teamfight["players"]):
                hero_id = self.player_number_to_hero_id.get(player_number, 0)
                self.parse_player_from_teamfight(player, hero_id, timeslot)

    def parse_player_from_teamfight(self, player, hero_id, timeslot):
        things_to_include_from_teamfights = self.experiment.variables["things_to_include_from_teamfights"]

        for thing in things_to_include_from_teamfights:
            list_of_edges_from_thing = list(player[thing].keys())
            self.add_edges_to_graph(hero_id, list_of_edges_from_thing, timeslot)

    def parse_player_items(self, items, hero_id):
        for item in items:
            timeslot = self.get_timeslot(item["time"])
            item_name = item["key"]
            self.add_edge_to_graph(hero_id, item_name, timeslot)

    def parse_player_summary(self):
        for player_number, player in enumerate(self.json["players"]):

            hero_id = self.player_number_to_hero_id.get(player_number, 0)
            things_to_include_from_player_summary = self.experiment.variables["things_to_include_from_player_summary"]

            for thing in things_to_include_from_player_summary:
                thing = player[thing]
                self.parse_player_items(thing, hero_id)

    def get_timeslot(self, timestamp):
        for i in range(len(self.timeslots)-1):
            start = self.timeslots[i]
            end = self.timeslots[i+1] - 1

            if start <= timestamp <= end:
                return i + 1
        return 0

    def add_edges_to_graph(self, hero_id, items, timeslot):
        for item in items:
            self.add_edge_to_graph(hero_id, item, timeslot)

    def add_edge_to_graph(self, node_1, node_2, timeslot):
        self.graph.add_edge(node_1, node_2, timeslot=timeslot)

    def get_hero_ids(self):
        hero_ids = [player["hero_id"] for player in self.json["players"]]
        for player_number, hero_id in enumerate(hero_ids):
            self.player_number_to_hero_id[player_number] = hero_id

    def build_sorted_edges(self):
        edges = self.graph.edges(data=True)
        self.sorted_edges = sorted(edges, key=lambda edge: edge[2]['timeslot'])

    def save_graph(self):
        self.build_sorted_edges()
        with open(self.graph_filename, 'w') as f:
            json.dump(self.sorted_edges, f)