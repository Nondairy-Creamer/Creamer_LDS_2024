## Bridging the gap between the connectome and whole-brain activity in C. elegans
https://doi.org/10.1101/2024.09.22.614271

Codebase for fitting and analyzing dynamical models from the paper

### Installation:
Clone the project

```git clone https://github.com/Nondairy-Creamer/Creamer_LDS_2024```

Set up your python environment with pip. Within that environment run

```pip install -e .```

All requirements are listed in the setup.py file if you want to install them manually

### Usage
The files in the quick_start_examples folder will show you how to load the models from the paper and use the models to predict STAMs, correlations, and reconstruct missing neurons.

If you would like to train a model on synthetic data, simply run main.txt. To see the available parameters for fitting and generating synethic data look at submission_params/syn_test.txt
