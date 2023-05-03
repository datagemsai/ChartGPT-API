import streamlit as st
from dotenv import load_dotenv
import os
from plotly.graph_objs._figure import Figure
import plotly.io as pio
import pandas as pd


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
    if not df_id in st.session_state:
        st.dataframe(self)
        st.session_state[df_id] = 1
    return ""
pd.DataFrame.display = lambda self: pd_display(self)
pd.DataFrame.__repr__ = lambda self: pd_display(self)
pd.DataFrame._repr_html_ = lambda self: pd_display(self)

# Monkey patching of Plotly show()
def st_show(self):
    import streamlit as st
    st.plotly_chart(self, use_container_width=True)
Figure.show = st_show
pio.show = st_show
