import pandas as pd
import streamlit as st
import json
import plotly.express as px
from app.auth import Login

from app.users import get_users, get_user_queries, get_user_charts
from app.charts import get_chart
from app.components.notices import Notices

# Show notices
Notices()

# Check user authentication
login = Login()

st.markdown("# Admin Dashboard")
if st.session_state["user_email"] not in [
    "ben@cadlabs.org",
    "konrad@cadlabs.org",
    "mrsharadgupta@gmail.com"
]:
    st.warning("You are not authorized to view this page.")
    st.stop()

# Allow user to select a user, and display the user email instead of the ID
st.markdown("## Users")
df_users = pd.DataFrame(get_users())
user_email = st.selectbox("Select a user", df_users["user_email"].tolist())
user_id = df_users[df_users["user_email"] == user_email]["id"].values[0]

# Create a Pandas dataframe of all users
st.dataframe(df_users)

# Create a Pandas dataframe of all queries for the selected user
st.markdown("## User Queries")
df_queries = pd.DataFrame(get_user_queries(user_id))
st.dataframe(df_queries)

# Create a Pandas dataframe of all charts for the selected user
st.markdown("## User Charts")
df_charts = pd.DataFrame(get_user_charts(user_id))
st.dataframe(df_charts)

# Set Pandas plotting backend to Plotly
pd.options.plotting.backend = "plotly" 

# Check if df_queries has any rows
if df_queries.shape[0] == 0:
    st.stop()

# Plot a stacked area chart with normalized values of the number of queries with status "PASSED" and "FAILED" per day
df_status_cumulative = df_queries.groupby("timestamp_start")["status"].value_counts().unstack().fillna(0).cumsum()

# Create a plot where "PASSED" is green and "FAILED" is red
# fig = df_status_cumulative.plot.area(stacked=True)
# st.plotly_chart(fig)

# Create the plot using Plotly Express
st.markdown("## Daily Usage")
fig = px.area(df_status_cumulative, facet_col="status", facet_col_wrap=1)
st.plotly_chart(fig)

# Using `timestamp_start` and `timestamp_end`, plot the distribution of query response times in seconds for the current user
st.markdown("## Query Response Times")
df_queries["response_time"] = pd.to_datetime(df_queries["timestamp_end"]) - pd.to_datetime(df_queries["timestamp_start"])
df_queries["response_time"] = df_queries["response_time"].dt.total_seconds()
fig = px.histogram(df_queries, x="response_time", nbins=100)
st.plotly_chart(fig)

# Using `number_of_steps`, plot the distribution of the number of steps in the query for the current user
st.markdown("## Query Number of Steps")
fig = px.histogram(df_queries, x="number_of_steps", nbins=100)
st.plotly_chart(fig)

# Using the Plotly chart `json` field, display all the user's Plotly charts
st.markdown("## User Charts")
for chart in get_user_charts(user_id):
    st.plotly_chart(json.loads(chart["json"]))

# Get details for a specific chart
st.markdown("## Chart Details")
chart_id = st.text_input("Chart ID", value="")
if chart_id:
    chart = get_chart(chart_id)
    if chart:
        st.plotly_chart(json.loads(chart["json"]))
        st.json(chart)
    else:
        st.info("Chart not found.")
