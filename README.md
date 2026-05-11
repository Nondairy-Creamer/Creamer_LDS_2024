# Bridging the gap between the connectome and whole-brain activity in C. elegans
https://doi.org/10.1101/2024.09.22.614271

Codebase for fitting and analyzing dynamical models from the paper

# Installation:
Clone the project

```git clone https://github.com/Nondairy-Creamer/Creamer_LDS_2026```

Set up your python environment with pip. Within that environment run

```pip install -e .```

All requirements are listed in the setup.py file if you want to install them manually.

`mpi4py` is one of the requirements and needs a working MPI runtime on your system before `pip install` will succeed. Install one first if you don't already have it:

- macOS: ```brew install open-mpi```
- Ubuntu / Debian: ```sudo apt install libopenmpi-dev openmpi-bin```
- Windows: install [Microsoft MPI](https://learn.microsoft.com/en-us/message-passing-interface/microsoft-mpi) (both the SDK and the runtime)

## Usage
The files in the `quick_start_examples` folder will show you how to load the models from the paper and use the models to predict STAMs, correlations, and reconstruct missing neurons.

If you would like to train a model on synthetic data, simply run ```main.py```. To see the available parameters for fitting and generating synethic data look at submission_params/syn_test.yml

`main.py` decides whether to submit to a cluster or run on the local machine. To see how the models are actually trained look at the ```fit_synthetic``` function in ```run_inference.py```

### Model files
You can see how to load the models in `quick_start_examples/predict_stams.py`
The models are an instantiation of the ssm class in `ssm_classes.py`
The class includes:

`dynamics_weights`: "W" - weight between every neuron in the brain.

`dynamics_input_weights`: "H" - effect of the opto stim on the targeted neuron.

`dynamics_cov`: "Q" - covariance of the dynamics noise. Diagonal in the paper.

`dynamics_input_lags`: size of the filters in dynamics_input_weights

`emissions_weights`: weights from latents to emissions. set to identity in the paper

`emissions_input_weights`: weights from inputs to emissions. set to 0 in the paper

`emissions_cov`: "R" - covariance of the emissions noise. Diagonal in the paper.

`emissions_input_lags`: number of lags in the input weights. not used in the paper

the parameters above also include their initial values with their name + _init

param_props is a dictionary with properties of the parameters

`mask`: binary mask which determines which values to learn. this is how we specify the connectome constraint

`shape`: any special shape parameters such as diagonal

`update`: whether or not to update this parameter during learning

### Connectome data
Connectome data was downloaded from [NemaNode](https://nemanode.org/) on November 1st, 2025. The following data sets are used and combined when constructing the connectome constraint:

- `white_1986_jsh.csv`
- `white_1986_n2u.csv`
- `witvliet_2020_7.csv`
- `witvliet_2020_8.csv`

These files live in `anatomical_data/worm_connectomes/` and are loaded by `load_anatomical_data` in `analysis_utilities.py`.

### Fitting experimental data
To fit a new model on the data from Randi et al 2023

Download the data from here: https://osf.io/qxhjd/
unzip the folder and place it somewhere convenient

modify submission_params/create_data_set.yml and change data_path: to the path of the saved data

run
```python create_data_set.py```

### Fitting locally (est time ~40 hours)
Take a look at submission_params/exp_test.yml. You can use this file to set the parameters of the model and the size of the data set. You can either edit exp_test or make a new .yml file with your own parameters.

To fit a model run

```python main.py submission_params/exp_test.yml```

Takes ~40 hours on a desktop to fit across 80 animals and 154 neurons.

If you want to run from your IDE without passing arguments, open `main.py` and edit the `param_name` assignment in the `if num_args == 1:` block (around line 104) so the active line points at the yml you want, e.g.:

```python
param_name = 'submission_params/exp_test.yml'
# param_name = 'submission_params/syn_test.yml'
```

Then run `main.py` in your preferred IDE.

### Fitting locally parallelized across CPUs (est time ~10 hours parallelized across 10 CPUs)
If you computer has multiple CPUs you can reduce computation time using mpi4py
First disable multithreading in numpy by running the following in the terminal

```export MKL_NUM_THREADS=1```

```export OMP_NUM_THREADS=1```

```export NUMEXPR_NUM_THREADS=1```

On Linux, to fit a model run
```mpiexec -n <num_cpus> python -m mpi4py main.py submission_params/exp_test.yml```

### Fit a model on an HPC cluster using SLURM (est time ~4 hours)
Examine submission_params/slurm_example.yml. Every entry in the slurm dict will be fed direclty to slurm. You can add / remove necessary commands as necessary

Note that this will depend on the exact specifications of your HPC cluster. You should be aware what size your nodes are to properly set 'cpus_per_task', 'tasks_per_node', and 'nodes'. Check main.py in the section after ```if 'slurm' in run_params.keys()``` to see how these are submitted.

Install the code according to instructions from the HPC specifications. Then run
```python main.py submission_params/slurm_example.yml```
