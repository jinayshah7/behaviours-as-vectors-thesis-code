from multiprocessing import Pool

from Experiment import Experiment
from VectorTrainingSampleGenerator import VectorTrainingSampleGenerator
from list_of_experiments import LIST_OF_EXPERIMENTS


def process(experiment_name):
    print(f"Current: {experiment_name}")
    experiment = Experiment(experiment_name)
    ve = VectorTrainingSampleGenerator(experiment)
    ve.generate_big_graph()
    ve.build_edge_list()
    ve.save_edges_for_tgn()
    ve.save_edges_for_node2vec()
    ve.save_edges_for_line()
    ve.save_edge_list()
    del ve


def main():
    with Pool(32) as p:
        p.map(process, LIST_OF_EXPERIMENTS)


if __name__ == '__main__':
    main()
