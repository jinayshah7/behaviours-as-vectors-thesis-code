from Experiment import Experiment
from VectorTrainingSampleGenerator import VectorTrainingSampleGenerator

EXPERIMENTS = [
    # "node2vec_variation_1",
    # "node2vec_variation_2",
    # "tgn_variation_1",
    # "tgn_variation_2",
    # "tgn_variation_3",
    # "tgn_variation_4",
    # "line",
    "trial4"
]


def main():

    for experiment_name in EXPERIMENTS:
        experiment = Experiment(experiment_name)

        if experiment.already_done():
            continue

        ve = VectorTrainingSampleGenerator(experiment)
        ve.generate_big_graph()
        ve.build_edge_list()
        ve.save_edges_for_tgn()
        ve.save_edges_for_node2vec()
        ve.save_edges_for_line()
        ve.save_edge_list()


if __name__ == '__main__':
    main()

