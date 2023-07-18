import streamlit as st
from dotenv import load_dotenv
import os
from plotly.graph_objs._figure import Figure
import plotly.io as pio
import pandas as pd
from pandas.io.formats import (
    format as fmt,
)
import firebase_admin
from io import StringIO
import logging
import json
from importlib import import_module


# Display app name
PAGE_NAME = "ChartGPT"
st.set_page_config(page_title=PAGE_NAME, page_icon="📈")

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables from .env
load_dotenv()
# If set, Streamlit secrets take preference over environment variables
os.environ.update(st.secrets)

ENV = os.environ.get("ENV", "LOCAL")

if ENV == "LOCAL":
    import app_secrets.gcp_service_accounts

if DEBUG := (os.getenv('DEBUG', 'false').lower() == 'true'):
    logger.warning("Application in debug mode, disable for production")
    fh = logging.FileHandler('logs/debug.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(fh)

if DISPLAY_USER_UPDATES := (os.getenv('DISPLAY_USER_UPDATES', 'false').lower() == 'true'):
    logger.info("User updates will be displayed")

if MAINTENANCE_MODE := (os.getenv('MAINTENANCE_MODE', 'false').lower() == 'true'):
    logger.info("Application in maintenance mode")

# Import sample question for project
datasets = import_module(f'app.config.{os.environ["PROJECT"].lower()}').datasets

# Initialise Google Cloud Firestore
if not firebase_admin._apps:
    try:
        if ENV == "LOCAL":
            cred = firebase_admin.credentials.Certificate(json.loads(os.environ['GCP_SERVICE_ACCOUNT']))
            _ = firebase_admin.initialize_app(cred)
        else:
            _ = firebase_admin.initialize_app()
    except ValueError as e:
        _ = firebase_admin.get_app(name='[DEFAULT]')

# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"

# Monkey patch the pandas DataFrame display method
def pd_display(self):
    import streamlit as st
    df_id = id(self)
    if df_id not in st.session_state:
        st.session_state["container"].text("")
        st.session_state["container"].dataframe(self)
        st.session_state["text"] = "\n\n"
        st.session_state["empty_container"] = st.session_state["container"].empty()
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

# TODO Determine if these patches are needed:
# pd.core.indexing._iLocIndexer.__repr__ = lambda self: pd_display(self)
# pd.core.indexing._iLocIndexer._repr_html_ = lambda self: pd_display(self)
# pd.core.indexing._LocIndexer.__repr__ = lambda self: pd_display(self)
# pd.core.indexing._LocIndexer._repr_html_ = lambda self: pd_display(self)

pd.core.frame.DataFrame.__repr__ = lambda self: pd_display(self)
pd.core.frame.DataFrame._repr_html_ = lambda self: pd_display(self)

def pandas_object_display(self):
    import streamlit as st
    df_id = id(self)
    if df_id not in st.session_state:
        st.session_state["container"].text("")
        st.session_state["container"].dataframe(self)
        st.session_state["text"] = "\n\n"
        st.session_state["empty_container"] = st.session_state["container"].empty()
        st.session_state[df_id] = 1

    return object.__repr__(self)

pd.core.base.PandasObject.__repr__ = lambda self: pandas_object_display(self)

def series_display(self):
    import streamlit as st
    df_id = id(self)
    if df_id not in st.session_state:
        st.session_state["container"].text("")
        st.session_state["container"].dataframe(self)
        st.session_state["text"] = "\n\n"
        st.session_state["empty_container"] = st.session_state["container"].empty()
        st.session_state[df_id] = 1

    repr_params = fmt.get_series_repr_params()
    return self.to_string(**repr_params)

pd.core.series.Series.__repr__ = lambda self: series_display(self)

# Monkey patching of Plotly show()
def st_show(self):
    import streamlit as st

    figure_id = id(self)
    if figure_id not in st.session_state:
        st.session_state["container"].plotly_chart(self, use_container_width=True)
        st.session_state["text"] = "\n\n"
        st.session_state["empty_container"] = st.session_state["container"].empty()
        st.session_state["messages"].append({"role": "assistant", "content": self, "type": "chart"})
        st.session_state[figure_id] = 1
        try:
            pio.templates.default = "plotly"
            self.update_layout(template=pio.templates.default)
            # TODO Enable for Discord bot
            # self.write_image(f'app/outputs/{figure_id}.png')
        except ValueError as e:
            logger.error(e)
    # return plotly.io.to_image(self, format="png")
    # return plotly.io.to_json(self)
    return "Plotly chart created and displayed successfully"

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
