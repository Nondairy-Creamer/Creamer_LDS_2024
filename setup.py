from setuptools import setup, find_packages

VERSION = '0.1.0'
DESCRIPTION = 'Companion code for https://doi.org/10.1101/2024.09.22.614271'

setup(
    name="Creamer_LDS_2026",
    version=VERSION,
    author="Matthew S. Creamer",
    description=DESCRIPTION,
    license="MIT",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'PyYAML',
    ],
    extras_require={
        # MPI parallelism for fitting on multi-core / multi-node machines.
        # Requires a working MPI runtime (e.g. OpenMPI or MPICH) on the system.
        'mpi': ['mpi4py'],
        # SLURM job submission helpers, only needed when dispatching to an HPC cluster.
        'slurm': ['simple-slurm'],
    },
    keywords=['python', 'calcium', 'ssm', 'linear', 'dynamical', 'system', 'lds'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
