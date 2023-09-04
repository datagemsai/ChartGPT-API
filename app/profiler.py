"""
Execute `python -m streamlit run app/profiler.py`
When complete, run `tuna app.profile`
"""

import cProfile

from app.Home import main

profiler = cProfile.Profile()
profiler.runctx("main()", globals(), locals())
profiler.dump_stats("app.profile")
