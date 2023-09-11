import json

import pandas as pd
import plotly.express as px
import streamlit as st

from app.auth import is_user_admin, requires_auth
from app.charts import get_chart
from app.components.notices import Notices
from app.users import UserCredits, get_user_charts, get_user_queries, get_users

# Show notices
Notices()


@requires_auth
def main(user_id, user_email):
    st.markdown("# Admin Dashboard")
    if not is_user_admin():
        st.warning("You are not authorized to view this page.")
        st.stop()

    with st.spinner("Loading..."):
        user_analytics_tab, user_tab, chart_tab = st.tabs(
            ["User Analytics", "User", "Chart"]
        )

        with user_analytics_tab:
            # Allow user to select a user, and display the user email instead of the ID
            st.markdown("## Users")
            df_users = pd.DataFrame(get_users())[["id", "user_email"]]

            # Add analytics to df_users
            df_users["number_of_queries"] = df_users["id"].apply(
                lambda user_id: len(get_user_queries(user_id))
            )
            df_users["number_of_charts"] = df_users["id"].apply(
                lambda user_id: len(get_user_charts(user_id))
            )
            df_users["active"] = (df_users["number_of_queries"] > 0) | (
                df_users["number_of_charts"] > 0
            )
            # Sort by number of queries
            df_users = df_users.sort_values(
                by=["number_of_queries"], ascending=False
            ).reset_index(drop=True)

            user_analytics_csv = df_users.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download user analytics as CSV",
                user_analytics_csv,
                "user_analytics.csv",
                "text/csv",
                key="download-csv",
            )

            # Display user analytics
            st.markdown(
                f"Active users: {df_users['active'].sum()} of {df_users.shape[0]} ({df_users['active'].sum()/df_users.shape[0]*100:.2f}%)"
            )
            st.markdown(
                f"Total number of queries: {df_users['number_of_queries'].sum()}"
            )
            st.markdown(f"Total number of charts: {df_users['number_of_charts'].sum()}")

            # Create a Pandas dataframe of all users
            st.dataframe(df_users)

        with user_tab:
            # User data
            st.markdown(f"## User: {user_email}")
            user_email = st.selectbox("Select a user", df_users["user_email"].tolist())
            user_id = df_users[df_users["user_email"] == user_email]["id"].values[0]

            # Display user credits and add option to add credits
            st.markdown("## User Credits")
            if not (
                user_credits := UserCredits.collection.get(
                    key=f"user_credits/{user_id}"
                )
            ):
                user_credits = UserCredits()
                user_credits.user_id = user_id
                user_credits.free_credits = 20
                user_credits.save()

            with st.form("user_credits"):
                st.write("Set number of free credits")
                current_free_credits = user_credits.free_credits
                updated_free_credits = st.number_input(
                    "Free credits", value=current_free_credits
                )
                submitted = st.form_submit_button("Save")
                if submitted:
                    user_credits.free_credits = updated_free_credits
                    user_credits.save()
                    st.success("Free credits updated!")

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
            df_status_cumulative = (
                df_queries.groupby("timestamp_start")["status"]
                .value_counts()
                .unstack()
                .fillna(0)
                .cumsum()
            )

            # Create a plot where "PASSED" is green and "FAILED" is red
            # fig = df_status_cumulative.plot.area(stacked=True)
            # st.plotly_chart(fig)

            # Create the plot using Plotly Express
            st.markdown("## Daily Usage")
            fig = px.area(df_status_cumulative, facet_col="status", facet_col_wrap=1)
            st.plotly_chart(fig)

            # Using `timestamp_start` and `timestamp_end`, plot the distribution of query response times in seconds for the current user
            st.markdown("## Query Response Times")
            df_queries["response_time"] = pd.to_datetime(
                df_queries["timestamp_end"]
            ) - pd.to_datetime(df_queries["timestamp_start"])
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

        with chart_tab:
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


if __name__ == "__main__":
    main()
