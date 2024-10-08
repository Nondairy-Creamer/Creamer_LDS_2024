import analysis_methods as am
from pathlib import Path
import pickle


# get held out RMDVR value
missing_neuron = 'RMDVR'

# missing_neuron_path = Path('/home/mcreamer/Documents/python/funcon_lds/trained_models/exp_DL4_IL45_N80_R0_Mrmdvr/20231018_184057')
missing_neuron_path = Path('/home/mcreamer/Documents/python/funcon_lds/trained_models/exp_DL4_IL45_N80_R0_synap_Mrmdvr/20240207_150122')
posterior_file = open(missing_neuron_path / 'posterior_test.pkl', 'rb')
posterior = pickle.load(posterior_file)
posterior_file.close()

rmdvr_index = posterior['cell_ids'].index(missing_neuron)
estimated_rmdvr = [i[:, rmdvr_index] for i in posterior['posterior']]

emissions_path = Path('/home/mcreamer/Documents/python/funcon_lds/trained_models/exp_DL4_IL45_N80_R0_synap/20231209_014019')
emissions_file = open(emissions_path / 'data_test.pkl', 'rb')
emissions = pickle.load(emissions_file)
emissions_file.close()

am.unmeasured_neuron(posterior['posterior'], posterior['cell_ids'], emissions['emissions'], emissions['cell_ids'], missing_neuron)