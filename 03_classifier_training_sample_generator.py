from Experiment import Experiment
from Vectors import Vectors
from TrainingSampleGenerator import TrainingSampleGenerator
from ClassifierTrainer import ClassifierTrainer

EXPERIMENTS = [
    # "4D",
    # "4D2",
    # "8D",
    # "16D"
    "128D"
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

        print(experiment.variables["vector_tag"])
        classifier = ClassifierTrainer(experiment)
        classifier.generate_result()


if __name__ == '__main__':
    main()
