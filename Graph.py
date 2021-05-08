import json
import os
import networkx as nx


class Graph:
    GRAPH_DIRECTORY = "game_graph_files"

    def __init__(self, game_id):
        self.id = game_id
        self.graph = nx.MultiGraph()
        self.graph_filename = f'{self.GRAPH_DIRECTORY}/{self.id}.graph'
        self.timeslots = []
        self.json = {}
        self.player_number_to_hero_id = {}
        self.sorted_edges = None

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
            print()

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
        ability_uses = list(player["ability_uses"].keys())
        item_uses = list(player["item_uses"].keys())

        self.add_edges_to_graph(hero_id, ability_uses, timeslot)
        self.add_edges_to_graph(hero_id, item_uses, timeslot)

    def parse_player_items(self, items, hero_id):
        for item in items:
            timeslot = self.get_timeslot(item["time"])
            item_name = item["key"]
            self.add_edge_to_graph(hero_id, item_name, timeslot)

    def parse_player_summary(self):
        for player_number, player in enumerate(self.json["players"]):

            hero_id = self.player_number_to_hero_id.get(player_number, 0)

            purchase_log = player["purchase_log"]
            kill_log = player["kills_log"]
            rune_log = player["runes_log"]

            self.parse_player_items(purchase_log, hero_id)
            self.parse_player_items(kill_log, hero_id)
            self.parse_player_items(rune_log, hero_id)

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
        print()
        hero_ids = [player["hero_id"] for player in self.json["players"]]
        for player_number, hero_id in enumerate(hero_ids):
            self.player_number_to_hero_id[player_number] = hero_id
        pass

    def build_sorted_edges(self):
        edges = self.graph.edges(data=True)
        self.sorted_edges = sorted(edges, key=lambda edge: edge[2]['timeslot'])

    def save_graph(self):
        self.build_sorted_edges()
        with open(self.graph_filename, 'w') as f:
            json.dump(self.sorted_edges, f)
