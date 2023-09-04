import datetime
import plotly.io as pio
import pandas as pd
from plotly.graph_objs._figure import Figure
from pandas.io.formats import (
    format as fmt,
)
from io import StringIO
from app.utils import copy_url_to_clipboard
from app import logger, db_charts, ENV


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
        chart_json = self.to_json()
        # Create new Firestore document with unique ID:
        chart_ref = db_charts.document()
        chart_ref.set(
            {
                "user_id": st.session_state.get("user_id", None),
                "user_email": st.session_state.get("user_email", None),
                "env": ENV,
                "query_metadata": st.session_state["query_metadata"],
                "timestamp": str(datetime.datetime.now()),
                "json": chart_json,
            }
        )
        chart_id = chart_ref.id
        # TODO Re-enable sharing of charts
        # st.session_state["container"].button('Copy chart URL', type="primary", key=chart_id, on_click=copy_url_to_clipboard, args=(f"/?chart_id={chart_id}",))
        st.session_state["text"] = "\n\n"
        st.session_state["empty_container"] = st.session_state["container"].empty()
        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": self,
                "type": "chart",
                "chart_id": chart_id,
            }
        )
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
