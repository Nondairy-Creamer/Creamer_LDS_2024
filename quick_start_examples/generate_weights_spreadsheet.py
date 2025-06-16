import numpy as np
import pickle
import csv


# load in the trained models from the paper
models = {}
model_file = open('models/connectome_constrained.pkl', 'rb')
model = pickle.load(model_file)
model_file.close()

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

with open('model_weights.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(csv_output)

