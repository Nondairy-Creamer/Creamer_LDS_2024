import os
import pickle
import csv

from _paths import EXAMPLES_DIR, MODELS_DIR

# load in the trained model from the paper
with open(os.path.join(MODELS_DIR, 'connectome_constrained.pkl'), 'rb') as model_file:
    model = pickle.load(model_file)

cell_ids = model.cell_ids.copy()
num_neurons = len(cell_ids)
weights = model.dynamics_weights.copy()
weights_mask = model.param_props['mask']['dynamics_weights'].copy()

csv_output = [['presynaptic cell', 'postsynaptic cell', 'weight']]

for i in range(num_neurons):
    for j in range(num_neurons):
        if i == j:
            continue

        if weights_mask[j, i]:
            csv_output.append([cell_ids[i], cell_ids[j], f"{weights[j, i]:.6f}"])

with open(os.path.join(EXAMPLES_DIR, 'model_weights.csv'), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(csv_output)

