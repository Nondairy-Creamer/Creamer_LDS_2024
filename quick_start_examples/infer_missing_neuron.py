import os
import pickle
import numpy as np
from matplotlib import pyplot as plt

from _paths import MODELS_DIR, DATA_DIR

# this file will take a recording of whole-brain activity from a worm and mask the activity
# of the neuron AVER. Then we will use the model and kalman smoothing to predict AVER's activity from the activity
# of all the other neurons.
# inference on a large model takes some time even on a single neuron so this may take ~10 minutes depending on the
# computer

chosen_neuron = 'AVER'
sister_neuron = 'AVEL'

# load in an example neural recording
with open(os.path.join(DATA_DIR, 'example_recording.pkl'), 'rb') as data_file:
    recording = pickle.load(data_file)

cell_ids = recording['cell_ids']
chosen_neuron_ind = cell_ids.index(chosen_neuron)
sister_neuron_ind = cell_ids.index(sister_neuron)

# load in the initial conditions of the data as inferred by the model
# these shouldn't matter much as they are only a single time point
with open(os.path.join(DATA_DIR, 'initial_conditions.pkl'), 'rb') as init_file:
    intial_conditions = pickle.load(init_file)

# load in the trained connectome_constrained model
with open(os.path.join(MODELS_DIR, 'connectome_constrained.pkl'), 'rb') as model_file:
    model = pickle.load(model_file)

# get the activity of AVER
activity_true = recording['activity'][:, chosen_neuron_ind].copy()

# mask the activity so the model can't use it when reconstructing
recording['activity'][:, chosen_neuron_ind] = np.nan

# also mask the bilaterally symmetric sister neuron
if sister_neuron is not None:
    recording['activity'][:, sister_neuron_ind] = np.nan

smoothed_means = model.lgssm_smoother(recording['activity'], recording['inputs'],
                                      intial_conditions['emissions_offset'],
                                      intial_conditions['init_mean'], intial_conditions['init_cov'])[1]

activity_inferred = smoothed_means[:, chosen_neuron_ind]

# plot the activity against each other
plt.figure()
plt.plot(activity_true, label='true activity')
plt.plot(activity_inferred, label='inferred activity')
plt.title(chosen_neuron + ' masked from recording')
plt.legend()
plt.show()
