import streamlit as st
from dotenv import load_dotenv
import os
from plotly.graph_objs._figure import Figure
import plotly.io as pio
import pandas as pd
from pandas.io.formats import (
    format as fmt,
)
from io import StringIO


# Load environment variables from .env
load_dotenv()
# If set, Streamlit secrets take preference over environment variables
os.environ.update(st.secrets)

DEBUG = (os.getenv('DEBUG', 'false').lower() == 'true')
if DEBUG: print("Application in debug mode, disable for production")

# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"

# Monkey patch the pandas DataFrame display method
def pd_display(self):
    import streamlit as st
    df_id = id(self)
    if df_id not in st.session_state:
        st.dataframe(self)
        st.session_state[df_id] = 1

    if self._info_repr():
        buf = StringIO()
        self.info(buf=buf)
        return buf.getvalue()

    repr_params = fmt.get_dataframe_repr_params()
    return self.to_string(**repr_params)

pd.DataFrame.display = lambda self: pd_display(self)
pd.DataFrame.__repr__ = lambda self: pd_display(self)
pd.DataFrame._repr_html_ = lambda self: pd_display(self)

pd.core.indexing._iLocIndexer.__repr__ = lambda self: pd_display(self)
pd.core.indexing._iLocIndexer._repr_html_ = lambda self: pd_display(self)

pd.core.indexing._LocIndexer.__repr__ = lambda self: pd_display(self)
pd.core.indexing._LocIndexer._repr_html_ = lambda self: pd_display(self)

pd.core.frame.DataFrame.__repr__ = lambda self: pd_display(self)
pd.core.frame.DataFrame._repr_html_ = lambda self: pd_display(self)

pd.core.series.Series.__repr__ = lambda self: pd_display(self)
pd.core.series.Series._repr_html_ = lambda self: pd_display(self)

pd.core.base.PandasObject.__repr__ = lambda self: pd_display(self)
pd.core.base.PandasObject._repr_html_ = lambda self: pd_display(self)

# Monkey patching of Plotly show()
def st_show(self):
    import streamlit as st
    figure_id = id(self)
    if figure_id not in st.session_state:
        st.plotly_chart(self, use_container_width=True)
        st.session_state[figure_id] = 1
    return "Plotly Figure created successfully"
Figure.show = st_show
pio.show = st_show
Figure.__repr__ = st_show

# TODO Find out how to make this work: Monkey patching of Python standard data type __repr__()
# def st_repr(self):
#     import streamlit as st
#     st.write(self)
#     return ""
# str.__repr__ = st_repr
# int.__repr__ = st_repr
# float.__repr__ = st_repr
