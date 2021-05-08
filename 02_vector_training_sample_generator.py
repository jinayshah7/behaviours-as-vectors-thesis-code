from Experiment import Experiment
from VectorTrainingSampleGenerator import VectorTrainingSampleGenerator

# make a loop for experiments
# save edges for tgn, nodevec, line separately
# all three will have a different format depending on the code
# also save the entity_id: entity_name file for each experiment

e = Experiment("trial4")
v = VectorTrainingSampleGenerator(e)
v.generate_big_graph()
v.build_edge_list()
v.save_edges_for_tgn()
v.save_edges_for_node2vec()


