from dataclasses import dataclass
import plotly.express as px
import pandas as pd
import streamlit as st

from fireo.models import Model
from fireo.fields import IDField, NumberField

from app import db_users, db_queries, db_charts


class UserCredits(Model):
    user_id: str = IDField()
    free_credits: int = NumberField()

def get_users():
    users = db_users.stream()
    return [{"id": user.id, **user.to_dict()} for user in users]

def get_user(user_id):
    user = db_users.document(user_id).get()
    return {"id": user.id, **user.to_dict()}

def get_user_queries(user_id):
    queries = db_queries.where("user_id", "==", user_id).stream()
    return [{"id": query.id, **query.to_dict()} for query in queries]

def get_user_charts(user_id):
    charts = db_charts.where("user_id", "==", user_id).stream()
    return [{"id": chart.id, **chart.to_dict()} for chart in charts]

def plot_daily_queries(user_id):
    # Get all queries for the user
    queries = get_user_queries(user_id)

    # Convert the 'timestamp' column to a datetime object
    df = pd.DataFrame(queries)
    df['timestamp_start'] = pd.to_datetime(df['timestamp_start'])

    # Group the queries by day and count the number of queries
    df_daily = df.groupby(pd.Grouper(key='timestamp_start', freq='D')).size().reset_index(name='count')

    # Create the Plotly chart
    fig = px.bar(df_daily, x='timestamp_start', y='count', title='Daily Usage')
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Number of Queries')

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
