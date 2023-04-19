import os
import sys
from dotenv import load_dotenv

import pandas as pd
from IPython import get_ipython

ipython = get_ipython()

# Find performance bottlenecks by timing Python cell execution
# ipython.magic("load_ext autotime") # ipython.magic("...") is equivalent to % in Jupyter cell

# Reload all modules (except those excluded by %aimport) every time before executing the Python code typed
# See https://ipython.org/ipython-doc/stable/config/extensions/autoreload.html
# ipython.magic("load_ext autoreload")
# ipython.magic("autoreload 2")

# Append the root directory to Python path,
# this allows you to store notebooks in `experiments/notebooks/` sub-directory and access model Python modules
sys.path.append("../")
sys.path.append("../..")
sys.path.append("../../..")
chpath = lambda depth_change=0, path=__file__: chpath(path=os.path.dirname(path), depth_change=depth_change-1) if depth_change >= 0 else os.chdir(path)
chpath(1)

# Configure Pandas to raise for chained assignment, rather than warn, so that we can fix the issue!
pd.options.mode.chained_assignment = 'raise'

# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"

# Load environment variables from .env file
load_dotenv()
