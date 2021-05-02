from Experiment import Experiment
from Vectors import Vectors
from TrainingSampleGenerator import TrainingSampleGenerator
from ClassifierTrainer import ClassifierTrainer


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

        vectors = Vectors(experiment)

        sample_generator = TrainingSampleGenerator(experiment, vectors)
        sample_generator.generate_samples()
        sample_generator.save_samples()

        classifier = ClassifierTrainer(experiment)
        classifier.generate_result()


if __name__ == '__main__':
    main()
