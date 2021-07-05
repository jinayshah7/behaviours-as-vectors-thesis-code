from Experiment import Experiment
from VectorTrainingSampleGenerator import VectorTrainingSampleGenerator
from list_of_experiments import LIST_OF_EXPERIMENTS


def main():

    for experiment_number, experiment_name in enumerate(LIST_OF_EXPERIMENTS):

        print(f"Completed - {experiment_number}/{len(LIST_OF_EXPERIMENTS)} - Current: {experiment_name}")
        experiment = Experiment(experiment_name)

        ve = VectorTrainingSampleGenerator(experiment)
        ve.generate_big_graph()
        ve.build_edge_list()
        ve.save_edges_for_tgn()
        ve.save_edges_for_node2vec()
        ve.save_edges_for_line()
        ve.save_edge_list()


if __name__ == '__main__':
    main()

