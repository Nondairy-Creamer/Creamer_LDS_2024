import numpy as np
import analysis_utilities as au
import matplotlib as mpl
from matplotlib import pyplot as plt
import pickle
from pathlib import Path
import metrics as met

colormap = mpl.colormaps['coolwarm']
plot_percent = 95
score_fun = met.nan_corr
# score_fun = met.nan_r2


def get_best_model(model_folders, sorting_param, use_test_data=True, plot_figs=True, best_model_ind=None):
    model_folders = [Path(i) for i in model_folders]
    model_list = []
    model_true_list = []
    posterior_train_list = []
    posterior_test_list = []

    for m in model_folders:
        m = 'trained_models' / m
        # load in the model and the data
        model_file = open(m / 'models' / 'model_trained.pkl', 'rb')
        model_list.append(pickle.load(model_file))
        model_file.close()

        model_true_path = m / 'models' / 'model_true.pkl'
        if model_true_path.exists():
            model_true_file = open(m / 'models' / 'model_true.pkl', 'rb')
            model_true_list.append(pickle.load(model_true_file))
            model_true_file.close()
        else:
            model_true_list.append(None)

        posterior_train_file = open(m / 'posterior_train.pkl', 'rb')
        posterior_train_list.append(pickle.load(posterior_train_file))
        posterior_train_file.close()

        posterior_test_file = open(m / 'posterior_test.pkl', 'rb')
        posterior_test_list.append(pickle.load(posterior_test_file))
        posterior_test_file.close()

    best_model_ind = plot_model_comparison(sorting_param, model_list, posterior_train_list, posterior_test_list,
                                           plot_figs=plot_figs, best_model_ind=best_model_ind)

    data_file = open('trained_models' / model_folders[best_model_ind] / 'data_train.pkl', 'rb')
    data_train = pickle.load(data_file)
    data_file.close()

    if 'data_corr' in data_train.keys():
        data_corr = data_train['data_corr']
    else:
        data_corr = au.nan_corr_data(data_train['emissions'])
        data_train['data_corr'] = data_corr

        data_file = open('trained_models' / model_folders[best_model_ind] / 'data_train.pkl', 'wb')
        pickle.dump(data_train, data_file)
        data_file.close()

    if use_test_data:
        data_file = open('trained_models' / model_folders[best_model_ind] / 'data_test.pkl', 'rb')
        data = pickle.load(data_file)
        data_file.close()

        posterior_dict = posterior_test_list[best_model_ind]
        data_path = 'trained_models' / model_folders[best_model_ind] / 'data_test.yml'
        posterior_path = 'trained_models' / model_folders[best_model_ind] / 'posterior_test.yml'
    else:
        data = data_train

        posterior_dict = posterior_train_list[best_model_ind]
        data_path = 'trained_models' / model_folders[best_model_ind] / 'data_train.yml'
        posterior_path = 'trained_models' / model_folders[best_model_ind] / 'posterior_train.yml'

    model = model_list[best_model_ind]
    model_true = model_true_list[best_model_ind]

    if type(data_corr) is tuple:
        data_corr = data_corr[0]

    return model, model_true, data, posterior_dict, data_path, posterior_path, data_corr


def plot_model_params(model, model_true=None, cell_ids_chosen=None):
    model_params = model.get_params()
    if model_true is not None:
        has_ground_truth = True
    else:
        has_ground_truth = False

    if cell_ids_chosen is None:
        cell_ids_chosen = model.cell_ids.copy()

    if has_ground_truth:
        model_params_true = model_true.get_params()
    cell_ids = model.cell_ids
    # limit the matrix to the chosen neurons
    neuron_inds_chosen = np.array([cell_ids.index(i) for i in cell_ids_chosen])

    # import lgssm_utilities as ssmu
    # conn = au.load_anatomical_data(cell_ids)
    # conn_mask = (conn['gap_conn'] + conn['chem_conn']) > 0
    # window = (15, 30)
    # cutoff_percent = 5
    # eirms = ssmu.calculate_eirms(model, window=window, verbose=True)
    # eirms_abs = np.abs(eirms)
    # cutoff = np.nanpercentile(eirms_abs, cutoff_percent)
    # connected = eirms_abs[conn_mask]
    # unconnected = eirms_abs[~conn_mask]
    #
    # plt.figure()
    # plt.subplot(1, 2, 1)
    # plot_max = np.nanpercentile(eirms_abs, 95)
    # bins = np.linspace(0, plot_max, 101)
    # plt.hist(connected, bins=bins, density=True, label='connected', alpha=0.5)
    # plt.hist(unconnected, bins=bins, density=True, label='unconnected', alpha=0.5)
    # plt.axvline(cutoff, linestyle='--', color='k')
    # plt.xlim((0, plot_max))
    # plt.legend()
    #
    # plt.subplot(1, 2, 2)
    # plot_x = np.arange(2)
    # plot_y = [np.sum(connected < cutoff) / np.sum(conn_mask), np.sum(unconnected < cutoff) / np.sum(~conn_mask)]
    # plt.bar(plot_x, plot_y)
    # plt.xticks(plot_x, ['connected', 'unconnected'])
    # plt.ylabel('frequency in bottom ' + str(cutoff_percent) + '%')
    # plt.tight_layout()
    #
    # plt.show()

    # plot the log likelihood
    plt.figure()
    plt.subplot(1, 2, 1)
    num_iter = np.arange(len(model.log_likelihood))
    plt.plot(num_iter, model.log_likelihood, label='fit parameters')
    if has_ground_truth:
        plt.axhline(model_true.log_likelihood[0], color='k', linestyle=':', label='true parameters')
        plt.legend()
    plt.xlabel('EM iteration')
    plt.ylabel('log likelihood')

    plt.subplot(1, 2, 2)
    subset = np.arange(int(len(num_iter) / 2), len(num_iter))
    plt.plot(num_iter[subset], [model.log_likelihood[i] for i in subset], label='fit parameters')
    if has_ground_truth:
        plt.axhline(model_true.log_likelihood[0], color='k', linestyle=':', label='true parameters')
        plt.legend()
    plt.xlabel('EM iteration')
    plt.ylabel('log likelihood')
    plt.tight_layout()
    plt.show()

    # plot the derivative of the log likelihood
    plt.figure()
    plt.subplot(1, 2, 1)
    num_iter = np.arange(len(model.log_likelihood)-1)
    ll_diff = np.diff(model.log_likelihood)
    plt.plot(num_iter, ll_diff, label='fit parameters')
    plt.xlabel('EM iteration')
    plt.ylabel('d/dt log likelihood')

    plt.subplot(1, 2, 2)
    subset = np.arange(int(len(num_iter) / 2), len(num_iter))
    plt.plot(num_iter[subset], [ll_diff[i] for i in subset], label='fit parameters')
    plt.xlabel('EM iteration')
    plt.ylabel('d/dt log likelihood')
    plt.tight_layout()
    plt.show()

    # plot the dynamics weights
    A_full = model_params['trained']['dynamics_weights'][:model.dynamics_dim, :]
    A = np.split(A_full, model.dynamics_lags, axis=1)
    A = [i[np.ix_(neuron_inds_chosen, neuron_inds_chosen)] for i in A]
    # get rid of the diagonal
    for aa in range(len(A)):
        A[aa][np.eye(A[aa].shape[0], dtype=bool)] = np.nan
    abs_max = np.nanmax(np.abs(A))

    if has_ground_truth:
        A_full_true = model_params_true['trained']['dynamics_weights'][:model.dynamics_dim, :]
        A_true = np.split(A_full_true, model.dynamics_lags, axis=1)
        A_true = [i[np.ix_(neuron_inds_chosen, neuron_inds_chosen)] for i in A_true]
        # get rid of the diagonal
        for aa in range(len(A_true)):
            A_true[aa][np.eye(A_true[aa].shape[0], dtype=bool)] = np.nan

        abs_max_true = np.nanmax(np.abs(A_true))
        abs_max = np.nanmax((abs_max, abs_max_true))
    else:
        A_true = [None for i in range(len(A))]

    for i in range(len(A)):
        plot_matrix(A[i], A_true[i], labels_x=cell_ids_chosen, labels_y=cell_ids_chosen, abs_max=abs_max, title='dynamics matrix')

    # plot the dynamics weights eigenvalues
    eigvals_trained, eigvects_trained = np.linalg.eig(model_params['trained']['dynamics_weights'])

    fig = plt.figure()
    x_circ = np.cos(np.linspace(0, 2 * np.pi, 100))
    y_circ = np.sin(np.linspace(0, 2 * np.pi, 100))

    if has_ground_truth:
        ax = plt.subplot(1, 2, 2)
        eigvals_true, eigvects_true = np.linalg.eig(model_params_true['trained']['dynamics_weights'])
        plt.scatter(np.real(eigvals_true), np.imag(eigvals_true))
        plt.plot(x_circ, y_circ)
        ax.set_aspect('equal', 'box')
        plt.title('true eigvals')
        ax = plt.subplot(1, 2, 1)
    else:
        ax = fig.add_subplot()

    plt.scatter(np.real(eigvals_trained), np.imag(eigvals_trained))
    plt.plot(x_circ, y_circ)
    ax.set_aspect('equal', 'box')
    plt.title('trained eigvals')

    plt.show()

    # plot the B matrix
    B_full = model_params['trained']['dynamics_input_weights'][:model.dynamics_dim, :]
    B = np.split(B_full, model.dynamics_input_lags, axis=1)
    B = np.stack([np.diag(i) for i in B]).T
    B = B[neuron_inds_chosen, :]

    if has_ground_truth:
        B_full_true = model_params_true['trained']['dynamics_input_weights'][:model.dynamics_dim, :]
        B_true = np.split(B_full_true, model.dynamics_input_lags, axis=1)
        B_true = np.stack([np.diag(i) for i in B_true]).T
        B_true = B_true[neuron_inds_chosen, :]
    else:
        B_true = None

    plot_matrix(B, B_true, labels_y=cell_ids_chosen, title='dynamics inputs (diagonal)')

    # plot the C matrix
    C_full = model_params['trained']['emissions_weights']
    C = np.split(C_full, model.dynamics_lags, axis=1)
    C = np.stack([np.diag(i) for i in C]).T
    C = C[neuron_inds_chosen, :]

    if has_ground_truth:
        C_full_true = model_params_true['trained']['emissions_weights']
        C_true = np.split(C_full_true, model.dynamics_lags, axis=1)
        C_true = np.stack([np.diag(i) for i in C_true]).T
        C_true = C_true[neuron_inds_chosen, :]
    else:
        C_true = None

    plot_matrix(C, C_true, labels_y=cell_ids_chosen, title='emissions weights')

    # Plot the Q matrix
    Q = model_params['trained']['dynamics_cov'][:model.dynamics_dim, :model.dynamics_dim]
    Q = Q[np.ix_(neuron_inds_chosen, neuron_inds_chosen)]

    if has_ground_truth:
        Q_true = model_params_true['trained']['dynamics_cov'][:model.dynamics_dim, :model.dynamics_dim]
        Q_true = Q_true[np.ix_(neuron_inds_chosen, neuron_inds_chosen)]
    else:
        Q_true = None

    plot_matrix(Q, Q_true, labels_x=cell_ids_chosen, labels_y=cell_ids_chosen, title='dynamics covariance')

    # Plot the R matrix
    R = model_params['trained']['emissions_cov']
    R = R[np.ix_(neuron_inds_chosen, neuron_inds_chosen)]

    if has_ground_truth:
        R_true = model_params_true['trained']['emissions_cov'][:model.dynamics_dim, :model.dynamics_dim]
        R_true = R_true[np.ix_(neuron_inds_chosen, neuron_inds_chosen)]
    else:
        R_true = None

    plot_matrix(R, R_true, labels_x=cell_ids_chosen, labels_y=cell_ids_chosen, title='emissions covariance')

    plt.show()

    return


def plot_matrix(param_trained, param_true=None, labels_x=None, labels_y=None, abs_max=None, title=''):
    # plot a specific model parameter, usually called by plot_model_params

    if abs_max is None:
        if param_true is not None:
            abs_max = np.nanmax([np.nanmax(np.abs(i)) for i in [param_trained, param_true, param_true - param_trained]])
        else:
            abs_max = np.nanmax([np.nanmax(np.abs(i)) for i in [param_trained]])

    if param_true is not None:
        plt.subplot(2, 2, 1)
    plt.imshow(param_trained, interpolation='Nearest', cmap=colormap)
    plt.title('fit weights, ' + title)
    plt.xlabel('input neurons')
    plt.ylabel('output neurons')
    plt.colorbar()
    plt.clim((-abs_max, abs_max))

    if labels_x is not None:
        plt.xticks(np.arange(param_trained.shape[1]), labels_x, rotation=90)

    if labels_y is not None:
        plt.yticks(np.arange(param_trained.shape[0]), labels_y)

    if param_true is not None:
        plt.subplot(2, 2, 2)
        plt.imshow(param_true, interpolation='Nearest', cmap=colormap)
        plt.title('true weights, ' + title)
        plt.clim((-abs_max, abs_max))
        plt.colorbar()

        if labels_x is not None:
            plt.xticks(np.arange(param_trained.shape[1]), labels_x, rotation=90)

        if labels_y is not None:
            plt.yticks(np.arange(param_trained.shape[0]), labels_y)

        plt.subplot(2, 2, 3)
        plt.imshow(param_true - param_trained, interpolation='Nearest', cmap=colormap)
        plt.title('true - fit')
        plt.clim((-abs_max, abs_max))
        plt.colorbar()

        if labels_x is not None:
            plt.xticks(np.arange(param_trained.shape[1]), labels_x, rotation=90)

        if labels_y is not None:
            plt.yticks(np.arange(param_trained.shape[0]), labels_y)

    plt.tight_layout()
    plt.show()

    return


def plot_sampled_model(data, posterior_dict, cell_ids, sample_rate=2, num_neurons=10,
                       window_size=1000, fig_save_path=None):
    emissions = data['emissions']
    inputs = data['inputs']
    posterior = posterior_dict['posterior']
    model_sampled = posterior_dict['model_sampled_noise']

    cell_ids_chosen = sorted(cell_ids['sorted'][:num_neurons])
    neuron_inds_chosen = np.array([cell_ids['all'].index(i) for i in cell_ids_chosen])

    # get all the inputs but with only the chosen neurons
    inputs_truncated = [i[:, neuron_inds_chosen] for i in inputs]
    emissions_truncated = [e[:, neuron_inds_chosen] for e in emissions]
    data_ind_chosen, time_window = au.get_example_data_set(inputs_truncated, emissions_truncated, window_size=window_size)

    emissions_chosen = emissions[data_ind_chosen][time_window[0]:time_window[1], neuron_inds_chosen]
    inputs_chosen = inputs[data_ind_chosen][time_window[0]:time_window[1], neuron_inds_chosen]
    all_inputs = inputs[data_ind_chosen][time_window[0]:time_window[1], :]
    posterior_chosen = posterior[data_ind_chosen][time_window[0]:time_window[1], neuron_inds_chosen]
    model_sampled_chosen = model_sampled[data_ind_chosen][time_window[0]:time_window[1], neuron_inds_chosen]

    stim_events = np.where(np.sum(all_inputs, axis=1) > 0)[0]
    stim_ids = [cell_ids['all'][np.where(all_inputs[i, :])[0][0]] for i in stim_events]

    filt_shape = np.ones(5)
    for i in range(inputs_chosen.shape[1]):
        inputs_chosen[:, i] = np.convolve(inputs_chosen[:, i], filt_shape, mode='same')

    plot_y = np.arange(len(cell_ids_chosen))
    plot_x = np.arange(0, emissions_chosen.shape[0], 60 * sample_rate)

    plt.figure()
    cmax = np.nanpercentile(np.abs((model_sampled_chosen, posterior_chosen)), plot_percent)

    plt.subplot(3, 1, 1)
    plt.imshow(inputs_chosen.T, interpolation='nearest', aspect='auto', cmap=colormap)
    plt.title('stimulation events')
    plt.yticks(plot_y, cell_ids_chosen)
    plt.xticks(plot_x, plot_x / sample_rate)
    plt.xlabel('time (s)')
    plt.clim((-1, 1))
    plt.colorbar()

    plt.subplot(3, 1, 2)
    plt.imshow(emissions_chosen.T, interpolation='nearest', aspect='auto', cmap=colormap)
    plt.clim((-cmax, cmax))
    plt.title('data')
    plt.yticks(plot_y, cell_ids_chosen)
    plt.xticks(plot_x, plot_x / sample_rate)
    plt.xlabel('time (s)')
    plt.colorbar()

    plt.subplot(3, 1, 3)
    plt.imshow(model_sampled_chosen.T, interpolation='nearest', aspect='auto', cmap=colormap)
    plt.clim((-cmax, cmax))
    plt.title('sampled model')
    plt.yticks(plot_y, cell_ids_chosen)
    plt.xticks(plot_x, plot_x / sample_rate)
    plt.xlabel('time (s)')
    plt.colorbar()

    plt.tight_layout()

    if fig_save_path is not None:
        plt.savefig(fig_save_path / 'emissions_vs_sampled.pdf')

    # plot the sampled model as time traces
    data_offset = -np.arange(emissions_chosen.shape[1])
    emissions_chosen = emissions_chosen + data_offset[None, :]
    model_sampled_chosen = model_sampled_chosen + data_offset[None, :]

    plt.figure()
    for stim_time, stim_name in zip(stim_events, stim_ids):
        plt.axvline(stim_time, color=[0.6, 0.6, 0.6], linestyle='--')
        plt.text(stim_time, 1.5, stim_name, rotation=90)
    plt.plot(emissions_chosen)
    plt.ylim([data_offset[-1] - 1, 1])
    plt.yticks(data_offset, cell_ids_chosen)
    plt.xticks(plot_x, (plot_x / sample_rate).astype(int))
    plt.xlabel('time (s)')
    plt.tight_layout()

    if fig_save_path is not None:
        plt.savefig(fig_save_path / 'emissions_time_traces.pdf')

    plt.figure()
    for stim_time, stim_name in zip(stim_events, stim_ids):
        plt.axvline(stim_time, color=[0.6, 0.6, 0.6], linestyle='--')
        plt.text(stim_time, 1.5, stim_name, rotation=90)
    plt.plot(model_sampled_chosen)
    plt.ylim([data_offset[-1] - 1, 1])
    plt.yticks(data_offset, cell_ids_chosen)
    plt.xticks(plot_x, (plot_x / sample_rate).astype(int))
    plt.xlabel('time (s)')
    plt.tight_layout()

    if fig_save_path is not None:
        plt.savefig(fig_save_path / 'model_sampled_time_traces.pdf')

    plt.show()

    return


def plot_missing_neuron(data, posterior_dict, sample_rate=2, fig_save_path=None):
    cell_ids = data['cell_ids']
    posterior_missing = posterior_dict['posterior_missing']
    emissions = data['emissions']
    rng = np.random.default_rng(0)

    # calculate the correlation of the missing to measured neurons
    missing_corr = np.zeros((len(emissions), emissions[0].shape[1]))
    for ei, pi in zip(range(len(emissions)), range(len(posterior_missing))):
        for n in range(emissions[ei].shape[1]):
            if np.mean(~np.isnan(emissions[ei][:, n])) > 0.5:
                missing_corr[ei, n] = met.nan_corr(emissions[ei][:, n], posterior_missing[ei][:, n])[0]
            else:
                missing_corr[ei, n] = np.nan

    # calculate a null distribution
    missing_corr_null = np.zeros((len(emissions), emissions[0].shape[1]))
    for ei, pi in zip(range(len(emissions)), range(len(posterior_missing))):
        random_assignment = rng.permutation(emissions[ei].shape[1])

        for n in range(emissions[ei].shape[1]):
            if np.mean(~np.isnan(emissions[ei][:, n])) > 0.5:
                missing_corr_null[ei, n] = met.nan_corr(emissions[ei][:, n], posterior_missing[ei][:, random_assignment[n]])[0]
            else:
                missing_corr_null[ei, n] = np.nan

    # get the p value that the reconstructed neuron accuracy is significantly different than the null
    p = au.single_sample_boostrap_p(missing_corr - missing_corr_null, n_boot=1000)

    plt.figure()
    plt.hist(missing_corr_null.reshape(-1), label='null', alpha=0.5)
    plt.hist(missing_corr.reshape(-1), label='missing data', alpha=0.5)
    plt.title('p = ' + str(p))
    plt.legend()
    plt.xlabel('correlation')
    plt.ylabel('count')

    if fig_save_path is not None:
        plt.savefig(fig_save_path / 'recon_histogram.pdf')

    sorted_corr_inds = au.nan_argsort(missing_corr.reshape(-1))
    best_offset = -3  # AVER
    median_offset = 5  # URYDL
    best_neuron = np.unravel_index(sorted_corr_inds[-1 + best_offset], missing_corr.shape)
    median_neuron = np.unravel_index(sorted_corr_inds[int(sorted_corr_inds.shape[0] / 2) + median_offset], missing_corr.shape)

    best_data_ind = best_neuron[0]
    best_neuron_ind = best_neuron[1]
    median_data_ind = median_neuron[0]
    median_neuron_ind = median_neuron[1]

    plot_x = np.arange(emissions[best_data_ind].shape[0]) / sample_rate
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.title('best held out neuron: ' + cell_ids[best_neuron_ind])
    plt.plot(plot_x, emissions[best_data_ind][:, best_neuron_ind], label='data')
    plt.plot(plot_x, posterior_missing[best_data_ind][:, best_neuron_ind], label='posterior')
    plt.xlabel('time (s)')
    plt.ylabel('neural activity')

    plot_x = np.arange(emissions[median_data_ind].shape[0]) / sample_rate
    # plot_x = np.arange(1000) * sample_rate
    plt.subplot(2, 1, 2)
    plt.title('median held out neuron: ' + cell_ids[median_neuron_ind])
    plt.plot(plot_x, emissions[median_data_ind][:, median_neuron_ind], label='data')
    plt.plot(plot_x, posterior_missing[median_data_ind][:, median_neuron_ind], label='posterior')
    plt.ylim(plt.ylim()[0], 1.2)
    plt.xlabel('time (s)')
    plt.ylabel('neural activity')

    plt.tight_layout()

    if fig_save_path is not None:
        plt.savefig(fig_save_path / 'recon_examples.pdf')

    plt.show()

    return


def plot_irm(model_weights, measured_irm, model_irm, data_corr, cell_ids, cell_ids_chosen, fig_save_path=None):
    chosen_neuron_inds = [cell_ids.index(i) for i in cell_ids_chosen]

    # get the combination of weights that looks most like the measured irm
    model_weights_norm = au.compare_matrix_sets(measured_irm, model_weights)[3]

    # sub sample the matricies down to the selected neurons
    data_corr = data_corr[np.ix_(chosen_neuron_inds, chosen_neuron_inds)]
    measured_irm = measured_irm[np.ix_(chosen_neuron_inds, chosen_neuron_inds)]
    model_irm = model_irm[np.ix_(chosen_neuron_inds, chosen_neuron_inds)]
    model_weights_norm = model_weights_norm[np.ix_(chosen_neuron_inds, chosen_neuron_inds)]

    # normalize the data for convenience in plotting
    data_corr = data_corr / np.nanmax(data_corr)
    measured_irm = measured_irm / np.nanmax(measured_irm)
    model_irm = model_irm / np.nanmax(model_irm)
    model_weights_norm = model_weights_norm / np.nanmax(model_weights_norm)

    # plot the average impulse responses of the chosen neurons
    plt.figure()
    plot_x = np.arange(len(chosen_neuron_inds))

    plt.subplot(2, 2, 1)
    plt.imshow(measured_irm, interpolation='nearest', cmap=colormap)
    plt.title('measured response')
    plt.xticks(plot_x, cell_ids_chosen, rotation=90)
    plt.yticks(plot_x, cell_ids_chosen)
    plt.clim((-1, 1))

    plt.subplot(2, 2, 2)
    plt.imshow(model_irm, interpolation='nearest', cmap=colormap)
    plt.title('model IRMs')
    plt.xticks(plot_x, cell_ids_chosen, rotation=90)
    plt.yticks(plot_x, cell_ids_chosen)
    plt.clim((-1, 1))

    plt.subplot(2, 2, 3)
    plt.imshow(data_corr, interpolation='nearest', cmap=colormap)
    plt.title('correlation')
    plt.xticks(plot_x, cell_ids_chosen, rotation=90)
    plt.yticks(plot_x, cell_ids_chosen)
    plt.clim((-1, 1))

    plt.subplot(2, 2, 4)
    plt.imshow(model_weights_norm, interpolation='nearest', cmap=colormap)
    plt.title('model weights')
    plt.xticks(plot_x, cell_ids_chosen, rotation=90)
    plt.yticks(plot_x, cell_ids_chosen)
    plt.clim((-1, 1))

    plt.tight_layout()

    if fig_save_path is not None:
        plt.savefig(fig_save_path / 'irms.pdf')

    plt.show()

    return


def compare_irm_w_anatomy(model_weights, measured_irm, model_irm, data_corr, cell_ids, cell_ids_chosen):
    chosen_neuron_inds = [cell_ids.index(i) for i in cell_ids_chosen]

    chem_conn, gap_conn, pep_conn = au.load_anatomical_data(cell_ids)

    # compare each of the weights against measured
    anatomy_list = [chem_conn, gap_conn, pep_conn]

    # get everything in magnitudes
    model_weights = [np.abs(i) for i in model_weights]
    measured_irm = np.abs(measured_irm)
    model_irm = np.abs(model_irm)
    data_corr = np.abs(data_corr)

    m = np.nansum(np.stack(model_weights), axis=0)
    m[np.isnan(measured_irm)] = np.nan

    measured_irm_score, measured_irm_score_ci, al_meas_l, al_meas_r = au.compare_matrix_sets(anatomy_list, measured_irm, positive_weights=True)
    model_irm_score, model_irm_score_ci, al_model_l, al_model_r = au.compare_matrix_sets(anatomy_list, model_irm, positive_weights=True)
    data_corr_score, data_corr_score_ci, al_corr_l, al_corr_r = au.compare_matrix_sets(anatomy_list, data_corr, positive_weights=True)
    model_weights_score, model_weights_score_ci, al_weights_l, al_weights_r = au.compare_matrix_sets(anatomy_list, model_weights, positive_weights=True)

    selected_neurons = np.ix_(chosen_neuron_inds, chosen_neuron_inds)
    anatomy_combined = [al_meas_l[selected_neurons], al_model_l[selected_neurons], al_corr_l[selected_neurons], al_weights_l[selected_neurons]]
    weights_combined = [al_meas_r[selected_neurons], al_model_r[selected_neurons], al_corr_r[selected_neurons], al_weights_r[selected_neurons]]
    name = ['measured IRMs', 'model IRMs', 'data corr', 'model weights']

    i = np.ix_(chosen_neuron_inds, chosen_neuron_inds)
    plot_x = np.arange(len(cell_ids_chosen))
    plt.figure()
    plt.subplot(2, 2, 1)
    plt.title('chemical synapses')
    plt.imshow(anatomy_list[0][i], cmap=colormap)
    cmax = np.max(np.abs(anatomy_list[0][i])).astype(float)
    plt.clim((-cmax, cmax))
    plt.xticks(plot_x, cell_ids_chosen, rotation=90)
    plt.yticks(plot_x, cell_ids_chosen)

    plt.subplot(2, 2, 2)
    plt.title('gap junctions')
    plt.imshow(anatomy_list[1][i], cmap=colormap)
    cmax = np.max(np.abs(anatomy_list[1][i]))
    plt.clim((-cmax, cmax))
    plt.xticks(plot_x, cell_ids_chosen, rotation=90)
    plt.yticks(plot_x, cell_ids_chosen)

    plt.subplot(2, 2, 3)
    plt.title('neuropeptide connectome')
    plt.imshow(anatomy_list[2][i], cmap=colormap)
    cmax = np.max(np.abs(anatomy_list[2][i]))
    plt.clim((-cmax, cmax))
    plt.tight_layout()
    plt.xticks(plot_x, cell_ids_chosen, rotation=90)
    plt.yticks(plot_x, cell_ids_chosen)

    for i in range(len(anatomy_combined)):
        plot_x = np.arange(len(cell_ids_chosen))
        plt.figure()
        plt.subplot(1, 2, 1)
        plt.imshow(anatomy_combined[i] / np.nanmax(anatomy_combined[i]), cmap=colormap)
        plt.clim((-1, 1))
        plt.xlabel('presynaptic')
        plt.ylabel('postsynaptic')
        plt.title('anatomy')
        plt.xticks(plot_x, cell_ids_chosen, rotation=90)
        plt.yticks(plot_x, cell_ids_chosen)

        plt.subplot(1, 2, 2)
        plt.imshow(weights_combined[i] / np.nanmax(weights_combined[i]), cmap=colormap)
        plt.clim((-1, 1))
        plt.title(name[i])
        plt.xlabel('presynaptic')
        plt.ylabel('postsynaptic')
        plt.xticks(plot_x, cell_ids_chosen, rotation=90)
        plt.yticks(plot_x, cell_ids_chosen)

        plt.tight_layout()

    # make figure comparing the metrics to the connectome
    plt.figure()
    plot_x = np.arange(3)
    y_val = np.array([data_corr_score, measured_irm_score, model_weights_score])
    y_val_ci = np.stack([data_corr_score_ci, measured_irm_score_ci, model_weights_score_ci]).T
    plt.bar(plot_x, y_val)
    plt.errorbar(plot_x, y_val, y_val_ci, fmt='.', color='k')
    plt.xticks(plot_x, ['data corr', 'measured IRM', 'model weights'])
    plt.ylabel('similarity to connectome')

    plt.show()

    return


def compare_measured_and_model_irm(model_weights, model_corr, measured_irm, model_irm, data_corr, cell_ids, cell_ids_chosen):
    neuron_inds_chosen = [cell_ids.index(i) for i in cell_ids_chosen]

    # grab the avereage impulse values that you want to plot
    measured_irm_chosen = measured_irm[np.ix_(neuron_inds_chosen, neuron_inds_chosen)]
    model_irm_chosen = model_irm[np.ix_(neuron_inds_chosen, neuron_inds_chosen)]
    data_corr_chosen = data_corr[np.ix_(neuron_inds_chosen, neuron_inds_chosen)]

    # scatter the interactions just between the chosen neurons
    model_sampled_score, model_sampled_score_ci = score_fun(measured_irm_chosen, model_irm_chosen)
    data_corr_score, data_corr_score_ci = score_fun(measured_irm_chosen, data_corr_chosen)

    plt.figure()
    plt.scatter(measured_irm_chosen.reshape(-1), model_irm_chosen.reshape(-1))
    xlim = plt.xlim()
    plt.plot(xlim, xlim)
    plt.title('model IRMs, ' + str(model_sampled_score))
    plt.ylabel('model IRMs')
    plt.xlabel('measured IRMs')

    plt.figure()
    plt.scatter(measured_irm_chosen.reshape(-1), data_corr_chosen.reshape(-1))
    plt.ylabel('data correlation')
    plt.xlabel('measured IRMs')
    plt.title('data correlation, ' + str(data_corr_score))

    data_corr_score, data_corr_score_ci = au.compare_matrix_sets(measured_irm, data_corr)[:2]
    model_sampled_score, model_sampled_score_ci = au.compare_matrix_sets(measured_irm, model_irm)[:2]
    model_weights_score, model_weights_score_ci = au.compare_matrix_sets(measured_irm, model_weights)[:2]

    # compare the metrics to the measured IRM
    plt.figure()
    plot_x = np.arange(3)
    y_val = np.array([data_corr_score, model_sampled_score, model_weights_score])
    y_val_ci = np.stack([data_corr_score_ci, model_sampled_score_ci, model_weights_score_ci]).T
    plt.bar(plot_x, y_val)
    plt.errorbar(plot_x, y_val, yerr=y_val_ci, fmt='.', color='k')
    plt.xticks(plot_x, ['data correlation', 'model IRMs', 'model weights'])
    plt.ylabel('similarity to measured IRMs')

    # show the scatter plots for the comparison to IRM
    plt.figure()
    plt.subplot(2, 2, 1)
    plt.scatter(measured_irm.reshape(-1), data_corr.reshape(-1), s=2)
    plt.ylabel('data correlation')
    plt.xlabel('measured IRMs')
    plt.subplot(2, 2, 2)
    plt.scatter(measured_irm.reshape(-1), model_irm.reshape(-1), s=2)
    xlim = plt.xlim()
    plt.plot(xlim, xlim, color='k')
    plt.ylabel('model IRMs')
    plt.xlabel('measured IRMs')
    plt.subplot(2, 2, 3)
    plt.scatter(model_irm.reshape(-1), data_corr.reshape(-1), s=2)
    plt.xlabel('model IRMs')
    plt.ylabel('data correlation')
    plt.tight_layout()

    data_corr_score, data_corr_score_ci = met.nan_corr(model_corr, data_corr)

    plt.figure()
    plt.subplot(1, 2, 1)
    plt.imshow(model_corr, interpolation='nearest')
    plt.subplot(1, 2, 2)
    plt.imshow(data_corr)

    plt.show()

    irm_scores = {'data_corr': [data_corr_score, data_corr_score_ci],
                  'model_sampled': [model_sampled_score, model_sampled_score_ci],
                  'model_weights': [model_weights_score, model_weights_score_ci]}

    return irm_scores


def plot_irf(measured_irf, measured_irf_sem, model_irf, cell_ids, cell_ids_chosen, window=(15, 30),
             sample_rate=2, num_plot=5, fig_save_path=None):

    chosen_neuron_inds = [cell_ids.index(i) for i in cell_ids_chosen]
    plot_x = np.arange(-window[0] * sample_rate, window[1] * sample_rate)

    # pull out the neurons we care about
    measured_irf = measured_irf[:, chosen_neuron_inds, :][:, :, chosen_neuron_inds]
    measured_irf_sem = measured_irf_sem[:, chosen_neuron_inds, :][:, :, chosen_neuron_inds]
    model_irf = model_irf[:, chosen_neuron_inds, :][:, :, chosen_neuron_inds]

    # find the 5 highest responses to plot
    measured_stim_responses_l2 = au.ave_fun(model_irf, axis=0)
    measured_stim_responses_l2[np.eye(measured_stim_responses_l2.shape[0], dtype=bool)] = 0
    sorted_vals = np.sort(measured_stim_responses_l2.reshape(-1))
    plot_inds = []
    for m in range(num_plot):
        best = np.where(measured_stim_responses_l2 == sorted_vals[-(m+1)])
        plot_inds.append((best[0][0], best[1][0]))

    measured_response_chosen = np.zeros((measured_irf.shape[0], num_plot))
    measured_response_sem_chosen = np.zeros((measured_irf.shape[0], num_plot))
    model_sampled_response_chosen = np.zeros((measured_irf.shape[0], num_plot))

    plot_label = []
    for pi, p in enumerate(plot_inds):
        measured_response_sem_chosen[:, pi] = measured_irf_sem[:, p[0], p[1]]
        measured_response_chosen[:, pi] = measured_irf[:, p[0], p[1]]
        model_sampled_response_chosen[:, pi] = model_irf[:, p[0], p[1]]
        plot_label.append((cell_ids_chosen[p[0]], cell_ids_chosen[p[1]]))

    ylim = (np.nanpercentile([measured_response_chosen - measured_response_sem_chosen, model_sampled_response_chosen], 1),
            np.nanpercentile([measured_response_chosen + measured_response_sem_chosen, model_sampled_response_chosen], 99))

    for i in range(measured_response_chosen.shape[1]):
        plt.figure()
        this_measured_resp = measured_response_chosen[:, i]
        this_measured_resp_sem = measured_response_sem_chosen[:, i]
        plt.plot(plot_x, this_measured_resp, label='measured')
        plt.fill_between(plot_x, this_measured_resp - this_measured_resp_sem, this_measured_resp + this_measured_resp_sem, alpha=0.4)
        plt.plot(plot_x, model_sampled_response_chosen[:, i], label='model sampled')
        plt.axvline(0, color='k', linestyle='--')
        plt.axhline(0, color='k', linestyle='--')
        plt.ylim(ylim)
        plt.ylabel(plot_label[i][0])
        plt.xlabel('time (s)')

        plt.legend()
        plt.title('average responses to stimulation of: ' + plot_label[i][1])

        if fig_save_path is not None:
            plt.savefig(fig_save_path / ('irf_' + str(i) + '.pdf'))

    plt.show()

    return


def plot_dynamics_eigs(model):
    A = model.dynamics_weights

    d_eigvals = np.linalg.eigvals(A)

    plt.figure()
    plt.plot(np.sort(np.abs(d_eigvals))[::-1])
    plt.ylabel('magnitude')
    plt.xlabel('eigen values')

    plt.figure()
    plt.scatter(np.real(d_eigvals), np.imag(d_eigvals), c=np.abs(d_eigvals), cmap=mpl.colormaps['YlOrRd'])
    plt.clim((0, 1))
    circ_t = np.linspace(0, 2*np.pi, 100)
    plt.plot(np.cos(circ_t), np.sin(circ_t), color='k')
    plt.xlabel('real components')
    plt.ylabel('imaginary components')
    plt.title('eigenvalues of the dynamics matrix')
    plt.xlim((-1.05, 1.05))
    plt.ylim((-1.05, 1.05))
    ax = plt.gca()
    ax.set_aspect('equal', 'box')

    plt.show()

    return


def plot_model_comparison(sorting_param, model_list, posterior_train_list, posterior_test_list,
                          plot_figs=True, best_model_ind=None):

    if sorting_param is not None:
        sorting_list = [getattr(i, sorting_param) for i in model_list]
    else:
        sorting_list = list(np.arange(len(model_list)))
        sorting_param = 'input order'

    for i in range(len(sorting_list)):
        if sorting_list[i] is None:
            sorting_list[i] = -np.inf
    ll_over_train = [getattr(i, 'log_likelihood') for i in model_list]
    train_ll = [i['ll'] for i in posterior_train_list]
    test_ll = [i['ll'] for i in posterior_test_list]

    if best_model_ind is None:
        best_model_ind = np.argmax(test_ll)

    if plot_figs:
        sorting_list_inds = np.argsort(sorting_list)
        sorting_list = np.sort(sorting_list)
        ll_over_train = [ll_over_train[i] for i in sorting_list_inds]
        train_ll = [train_ll[i] for i in sorting_list_inds]
        test_ll = [test_ll[i] for i in sorting_list_inds]

        plt.figure()
        for ii, i in enumerate(ll_over_train):
            num_iter = len(i)
            iter_x = np.arange(num_iter)
            plt.subplot(1, 2, 1)
            plt.plot(iter_x, i, label=sorting_param + ': ' + str(sorting_list[ii]))
            plt.xlabel('Iterations of EM')
            plt.ylabel('log likelihood')
            plt.subplot(1, 2, 2)
            plt.plot(iter_x[int(num_iter / 2):], i[int(num_iter / 2):], label=sorting_param + ': ' + str(sorting_list[ii]))
            plt.xlabel('Iterations of EM')
            plt.ylabel('log likelihood')

        plt.subplot(1, 2, 1)
        plt.legend()
        plt.tight_layout()

        if sorting_list[0] == -np.inf:
            sorting_list[0] = 2 * sorting_list[1] - sorting_list[2]
        plt.figure()
        plt.subplot(1, 2, 1)
        plt.plot(sorting_list, train_ll, label='train', marker='o')
        plt.xlabel(sorting_param)
        plt.ylabel('log likelihood')
        plt.grid()
        plt.subplot(1, 2, 2)
        plt.plot(sorting_list, test_ll, label='test', marker='o')
        plt.xlabel(sorting_param)
        plt.grid()
        plt.tight_layout()

        plt.show()

    return best_model_ind


def unmeasured_neuron(posterior, posterior_ids, emissions, emissions_ids, missing_neuron):
    rmdvr_index_missing = posterior_ids.index(missing_neuron)
    estimated_rmdvr = [i[:, rmdvr_index_missing] for i in posterior]

    rmdvr_index_true = emissions_ids.index(missing_neuron)
    true_rmdvr = [i[:, rmdvr_index_true] for i in emissions]

    # measure similarities between estimated and true RMDVR activity
    score = np.nanmean([met.nan_corr(i, j)[0] for i, j in zip(true_rmdvr, estimated_rmdvr)])

    null = []
    # make a null distribution
    for n in range(len(emissions_ids)):
        if n != rmdvr_index_true:
            random_neuron = [i[:, n] for i in emissions]
            score_for_random_neuron = [met.nan_corr(i, j)[0] for i, j in zip(random_neuron, estimated_rmdvr)]
            null.append(np.nanmean(score_for_random_neuron))

    p_value = np.mean(score < null)

    plt.figure()
    plt.hist(null, label='Estimation of RMDVR vs random neuron')
    plt.axvline(score, label='Estimation of ' + missing_neuron + ' vs true', color='k', linestyle='--')
    plt.xlabel('average correlation')
    plt.ylabel('# of neurons')
    plt.title('Estimation of ' + missing_neuron + ' when its activity is not measured\n p=' + str(p_value))
    plt.legend()

    plt.show()

    return
