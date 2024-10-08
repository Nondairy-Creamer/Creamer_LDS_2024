import numpy as np
# import wormneuroatlas as wa
import pickle
from pathlib import Path
import metrics as met
import itertools
import csv


def auto_select_ids(inputs, cell_ids, num_neurons=10):
    num_stim = np.sum(np.stack([np.sum(i, axis=0) for i in inputs]), axis=0)
    top_stims = np.argsort(num_stim)[-num_neurons:]
    cell_ids_chosen = [cell_ids[i] for i in top_stims]

    return cell_ids_chosen


def nan_argsort(data):
    sorted_inds = np.argsort(data)
    sorted_inds = sorted_inds[~np.isnan(data[sorted_inds])]
    return sorted_inds


def p_norm(data, power=1, axis=None):
    return np.nanmean(np.abs(data)**power, axis=axis)**(1/power)


def ave_fun(data, axis=None):
    return np.nanmean(data, axis=axis)


def nan_convolve(data, filter, mode='valid'):
    # attempt to ignore nans during a convolution
    # this isn't particularly principled, will just replace nans with 0s and divide the convolution
    # by the fraction of data that was in the window
    # only makes sense for nonnegative filters

    if np.any(filter < 0):
        raise Exception('nan_filter can only handle nonnegative filters')

    nan_loc = np.isnan(data)
    data_no_nan = data
    data_no_nan[nan_loc] = 0
    data_filtered = np.convolve(data_no_nan, filter, mode=mode)
    nan_count = np.convolve(~nan_loc, filter / np.sum(filter), mode=mode)
    nan_count[nan_count == 0] = 1
    data_nan_conv = data_filtered / nan_count

    nan_loc_pad = np.zeros(filter.size - 1) == 0
    nan_loc = np.concatenate((nan_loc, nan_loc_pad))
    nan_loc = nan_loc[:data_filtered.shape[0]]
    data_nan_conv[nan_loc] = np.nan

    return data_nan_conv


def stack_weights(weights, num_split, axis=-1):
    return np.stack(np.split(weights, num_split, axis=axis))


def load_anatomical_data(cell_ids=None):
    # load in anatomical data
    chem_path = Path('anatomical_data/chemical.pkl')
    if not chem_path.exists():
        chem_path = Path('../') / chem_path
    chem_file = open(chem_path, 'rb')
    chemical_synapse_connectome = pickle.load(chem_file)
    chem_file.close()

    gap_path = Path('anatomical_data/gap.pkl')
    if not gap_path.exists():
        gap_path = Path('../') / gap_path
    gap_file = open(gap_path, 'rb')
    gap_junction_connectome = pickle.load(gap_file)
    gap_file.close()

    peptide_path = Path('anatomical_data/peptide.pkl')
    if not peptide_path.exists():
        peptide_path = Path('../') / peptide_path
    peptide_file = open(peptide_path, 'rb')
    peptide_connectome = pickle.load(peptide_file)
    peptide_file.close()

    # syn_size_connectome = load_synapse_size(cell_ids.copy())

    ids_path = Path('anatomical_data/cell_ids.pkl')
    if not ids_path.exists():
        ids_path = Path('../') / ids_path
    ids_file = open(ids_path, 'rb')
    atlas_ids = pickle.load(ids_file)
    ids_file.close()

    if cell_ids is not None:
        if '0' in cell_ids:
            # if the data is synthetic just choose the first n neurons for testing
            atlas_inds = np.arange(len(cell_ids))
        else:
            atlas_inds = [atlas_ids.index(i) for i in cell_ids]

        chemical_synapse_connectome = chemical_synapse_connectome[np.ix_(atlas_inds, atlas_inds)]
        gap_junction_connectome = gap_junction_connectome[np.ix_(atlas_inds, atlas_inds)]
        peptide_connectome = peptide_connectome[np.ix_(atlas_inds, atlas_inds)]

    anatomy_dict = {'chem_conn': chemical_synapse_connectome,
                    'gap_conn': gap_junction_connectome,
                    'pep_conn': peptide_connectome}

    return anatomy_dict


def load_synapse_size(cell_ids):
    syn_size_path = Path('anatomical_data/cook_synapse_size_connectome.csv')
    if not syn_size_path.exists():
        syn_size_path = Path('../') / syn_size_path

    cell_ids[cell_ids.index('DA1')] = 'DA01'
    cell_ids[cell_ids.index('DB1')] = 'DB01'
    cell_ids[cell_ids.index('DB2')] = 'DB02'
    cell_ids[cell_ids.index('DD1')] = 'DD01'
    cell_ids[cell_ids.index('VA1')] = 'VA01'
    cell_ids[cell_ids.index('VB1')] = 'VB01'
    cell_ids[cell_ids.index('VB2')] = 'VB02'

    num_neurons = len(cell_ids)
    with open(syn_size_path, 'r') as f:
        synapse_size_data_in = list(csv.reader(f, delimiter=","))

    postsynaptic_cell_ids = synapse_size_data_in[2][3:]
    synapse_size_data = synapse_size_data_in[3:-1]
    presynaptic_cell_ids = [i[2] for i in synapse_size_data]
    synapse_size_data = [i[3:-1] for i in synapse_size_data]
    synapse_size_data = np.array(synapse_size_data)
    synapse_size_data[synapse_size_data == ''] = '0'
    synapse_size_data = synapse_size_data.astype(int)

    synapse_size = np.zeros((num_neurons, num_neurons))
    postsynaptic_cell_indicies = np.zeros(num_neurons, dtype=int)
    for ii, i in enumerate(cell_ids):
        postsynaptic_cell_indicies[ii] = postsynaptic_cell_ids.index(i)

    for ii, i in enumerate(cell_ids):
        synapse_size[ii, :] = synapse_size_data[presynaptic_cell_ids.index(i), postsynaptic_cell_indicies]

    return synapse_size


# def get_anatomical_data(cell_ids):
#     # load in anatomical data
#     watlas = wa.NeuroAtlas()
#     atlas_ids = list(watlas.neuron_ids)
#     chemical_connectome_full = watlas.get_chemical_synapses()
#     gap_junction_connectome_full = watlas.get_gap_junctions()
#     peptide_connectome_full = watlas.get_peptidergic_connectome()
#     atlas_ids[atlas_ids.index('AWCON')] = 'AWCR'
#     atlas_ids[atlas_ids.index('AWCOFF')] = 'AWCL'
#     atlas_inds = [atlas_ids.index(i) for i in cell_ids]
#     chem_conn = chemical_connectome_full[np.ix_(atlas_inds, atlas_inds)]
#     gap_conn = gap_junction_connectome_full[np.ix_(atlas_inds, atlas_inds)]
#     pep_conn = peptide_connectome_full[np.ix_(atlas_inds, atlas_inds)]
#
#     return chem_conn, gap_conn, pep_conn


def interleave(a, b):
    c = np.empty(a.size + b.size, dtype=a.dtype)
    c[0::2] = a
    c[1::2] = b

    return c


def get_sister_cell(chosen_cell, cell_ids):
    if chosen_cell[-1] == 'L':
        sister_cell = chosen_cell[:-1] + 'R'
    elif chosen_cell[-1] == 'R':
        sister_cell = chosen_cell[:-1] + 'L'
    else:
        sister_cell = None

    if sister_cell not in cell_ids:
        sister_cell = None

    return sister_cell


def get_example_data_set_simple(inputs, emissions, neuron_ind, cell_ids, sample_rate):
    from matplotlib import pyplot as plt
    # consider 1, (1717) <- good
    # 3 (2457, 2519)
    # 4 (2120)
    # 5 (2120)

    chosen_ind = 1
    stim_ind = 1717
    num_time = 480 * sample_rate
    chosen_window = (int(stim_ind - num_time / 2), int(stim_ind + num_time / 2))

    for ii, (i, e) in enumerate(zip(inputs, emissions)):
        stim_locations = np.where(i[:, neuron_ind])[0]

        for sl in stim_locations:
            range_to_plot = (int(sl - num_time / 2), int(sl + num_time / 2))
            snip = e[range_to_plot[0]:range_to_plot[1], :]
            if np.any(np.isnan(snip)):
                continue

            if snip.shape[0] < num_time / 2:
                continue
            #
            # plt.figure()
            # plt.imshow(snip.T)
            # plt.show()

    return chosen_ind, chosen_window


def get_example_data_set(inputs, mask=None, emissions=None, chosen_neuron_ind=None, window_size=1000):
    max_data_set = 0
    max_ind = 0
    max_val = 0
    max_window = 0

    for ii, i in enumerate(inputs):
        # some data sets might be smaller than window size
        this_window_size = np.min((window_size, i.shape[0]))

        # we're going to pass a square filter over the data to find the locations with the most stimulation events
        t_filt = np.ones(this_window_size)
        inputs_filtered = np.zeros((i.shape[0] - this_window_size + 1, i.shape[1]))

        for n in range(i.shape[1]):
            inputs_filtered[:, n] = np.convolve(i[:, n], t_filt, mode='valid')

        # sum the filtered inputs over neurons
        total_stim = inputs_filtered.sum(1)

        if chosen_neuron_ind is not None:
            recording_has_neuron = np.mean(np.isnan(emissions[ii][:, chosen_neuron_ind]), axis=0) < 0.3
            total_stim = total_stim * recording_has_neuron

        if emissions is not None:
            # check that all the neurons are measured
            e = emissions[ii]
            has_emissions = np.all(np.mean(np.isnan(e), axis=0) < 0.5)
        else:
            has_emissions = True

        this_max_val = np.max(total_stim)
        this_max_ind = np.argmax(total_stim)

        if (ii == 0) or (this_max_val > max_val and has_emissions):
            max_val = this_max_val
            max_ind = this_max_ind
            max_data_set = ii
            max_window = this_window_size
            print(ii)

    time_window = (max_ind, max_ind + max_window)

    return max_data_set, time_window


def condensed_distance(mat):
    def ave_nan_dist(x, y):
        return np.nanmean(np.sqrt(x**2 + y**2))

    dist = []

    for i in itertools.combinations(range(mat.shape[0]), 2):
        m1 = mat[i[0], :]
        m2 = mat[i[1], :]
        dist.append(ave_nan_dist(m1, m2))

    return dist


def normalize_model(model, posterior=None, init_mean=None, init_cov=None):
    c_sum = model.emissions_weights.sum(1)
    c_sum_stacked = np.tile(c_sum, model.dynamics_lags)
    h = np.diag(c_sum_stacked)
    h_inv = np.diag(1 / c_sum_stacked)

    model.dynamics_weights = h @ model.dynamics_weights @ h_inv
    model.dynamics_input_weights = h @ model.dynamics_input_weights
    model.dynamics_cov = h @ model.dynamics_cov @ h.T

    model.emissions_weights = model.emissions_weights @ h_inv

    if posterior is not None:
        posterior = [i @ h[:model.dynamics_dim, :model.dynamics_dim].T for i in posterior]

    if init_mean is not None:
        init_mean = [h @ i for i in init_mean]

    if init_cov is not None:
        init_cov = [h @ i @ h.T for i in init_cov]

    return model, posterior, init_mean, init_cov


def nan_corr_data(data, alpha=0.05):
    data_cat = np.concatenate(data, axis=0)
    data_corr = np.zeros((data_cat.shape[1], data_cat.shape[1]))
    data_corr_ci = np.zeros((2, data_cat.shape[1], data_cat.shape[1]))

    for i in range(data_cat.shape[1]):
        for j in range(data_cat.shape[1]):
            data_corr[i, j], data_corr_ci[:, i, j] = met.nan_corr(data_cat[:, i], data_cat[:, j], alpha=alpha)

        print(i+1, '/', data_cat.shape[1], 'neurons correlated')

    return data_corr, data_corr_ci


def get_neuron_types(cell_ids):
    file_name = Path('anatomical_data/neuron_type.csv')
    if ~file_name.exists():
        file_name = Path('..') / file_name
    neuron_types_str = np.loadtxt(file_name, delimiter=',', dtype=str, usecols=[0, 1])

    file_cell_names = list(neuron_types_str[:, 0])
    file_cell_descriptions = list(neuron_types_str[:, 1])

    cell_classifications = ['Sensory', 'Interneuron', 'Modulatory', 'Motor', 'Pharynx']
    neuron_types = np.zeros((len(cell_ids), len(cell_classifications))).astype(bool)

    for cfni, cfn in enumerate(file_cell_names):
        for cii, ci in enumerate(cell_ids):
            if cfn in ci:
                cell_description = file_cell_descriptions[cfni]

                for cci, cc in enumerate(cell_classifications):
                    if cc in cell_description:
                        neuron_types[cii, cci] = True

    return neuron_types, cell_classifications


def get_neurotransmitters(cell_ids):
    file_name = Path('anatomical_data/neurotransmitters.csv')
    if ~file_name.exists():
        file_name = Path('..') / file_name

    neuron_types_str = np.loadtxt(file_name, delimiter=',', dtype=str, usecols=[1, 2])

    file_cell_names = list(neuron_types_str[:, 0])
    file_cell_descriptions = list(neuron_types_str[:, 1])

    is_gabaergic = np.zeros(len(cell_ids)).astype(bool)

    for cii, ci in enumerate(cell_ids):
        if ci in file_cell_names:
            file_index = file_cell_names.index(ci)

        cell_description = file_cell_descriptions[file_index]
        is_gabaergic[cii] = cell_description == 'GABA'

    return is_gabaergic


def single_sample_boostrap_p(data, metric=np.mean, n_boot=10000, rng=np.random.default_rng()):
    booted_metric = np.zeros(n_boot)

    # get rid of nans
    data = data.reshape(-1).astype(float)
    data = data[~np.isnan(data)]

    for n in range(n_boot):
        sample_inds = rng.integers(0, high=data.shape[0], size=data.shape[0])
        data_resampled = data[sample_inds]
        booted_metric[n] = metric(data_resampled)

    if np.median(booted_metric) < 0:
        booted_metric *= -1

    p = 2 * np.mean(booted_metric <= 0)

    return p

