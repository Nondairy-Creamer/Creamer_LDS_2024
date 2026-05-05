"""Path bootstrap shared by all quick_start_examples scripts.

Importing this module:
1. Adds the project root to sys.path so pickle.load can resolve top-level
   modules like `ssm_classes`, `lgssm_utilities`, etc., regardless of the
   current working directory.
2. Exposes PROJECT_ROOT, MODELS_DIR, and DATA_DIR so scripts can build
   absolute paths instead of relying on the caller's CWD.
"""

import os
import sys

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
