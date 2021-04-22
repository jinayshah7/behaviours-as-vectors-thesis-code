import json
import os


class Graph:
    GRAPH_DIRECTORY = "game_graph_files"

    def __init__(self, id):
        self.id = id
        self.graph = {}
        self.graph_filename = f'{self.GRAPH_DIRECTORY}/{self.id}.graph'
        self.timeslots = []
        self.json = {}
        self.player_number_to_hero_id = {}

    def build(self, json):
        self.json = json
        if self.already_exists():
            self.load_graph_from_file()

        self.build_timeslots()
        self.get_hero_ids()
        self.parse_player_summary()
        self.parse_teamfights()

    def load_graph_from_file(self):
        with open(self.graph_filename) as f:
            file_json_data = json.load(f)
            edges = file_json_data["edges"]

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
                hero_id = self.player_number_to_hero_id[player_number]
                self.parse_player_from_teamfight(player, hero_id, timeslot)

    def parse_player_from_teamfight(self, player, hero_id, timeslot):
        ability_uses = list(player["ability_uses"].keys())
        item_uses = list(player["item_uses"].keys())

        self.add_edges_to_graph(hero_id, ability_uses, timeslot)
        self.add_edges_to_graph(hero_id, item_uses, timeslot)

    def parse_player_items(self, items, hero_id):
        for item in items:
            timeslot = self.get_timeslot(item["time"])
            item_name = item["name"]
            self.add_edge_to_graph(hero_id, item_name, timeslot)

    def parse_player_summary(self):
        for player_number, player in enumerate(self.json["players"]):

            hero_id = self.player_number_to_hero_id[player_number]

            purchase_log = player["purchase_log"]
            kill_log = player["kills_log"]
            rune_log = player["runes_log"]

            self.parse_player_items(purchase_log, hero_id)
            self.parse_player_items(kill_log, hero_id)
            self.parse_player_items(rune_log, hero_id)

    def get_timeslot(self, timestamp):
        for i in range(len(self.timeslots)-1):
            start = self.timeslots[i]
            end = self.timeslots[i] - 1

            if start <= timestamp <= end:
                return i

    def add_edges_to_graph(self, hero_id, items, timeslot):
        for item in items:
            self.add_edge_to_graph(hero_id, item, timeslot)

    def add_edge_to_graph(self, node_1, node_2, timeslot):
        pass

    def get_hero_ids(self):
        pass
