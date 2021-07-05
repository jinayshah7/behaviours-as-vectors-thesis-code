from Experiment import Experiment
from Vectors import Vectors
from TrainingSampleGenerator import TrainingSampleGenerator
from ClassifierTrainer import ClassifierTrainer
from list_of_experiments import LIST_OF_EXPERIMENTS


def main():
    for experiment_name in LIST_OF_EXPERIMENTS:
        experiment = Experiment(experiment_name)

        # if experiment.already_done():
        #     continue

        vectors = Vectors(experiment)

        sample_generator = TrainingSampleGenerator(experiment, vectors)
        sample_generator.generate_samples()
        sample_generator.save_samples()

        print(experiment.variables["vector_tag"])
        classifier = ClassifierTrainer(experiment)
        classifier.generate_result()
        classifier.save_result()


if __name__ == '__main__':
    main()
