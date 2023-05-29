# 2023-05-25
#  query = """
#  SELECT collection_name, nft_collateral_contract as address, AVG(apr) as mean, APPROX_QUANTILES(apr, 2)[OFFSET(1)] as median, STDDEV(apr) as std, COUNT(*) as count, SUM(usd_value) as borrow_volume
#  FROM `nftfi_loan_data.nftfi_loan_data`
#  WHERE date >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)) AND apr <= 200
#  GROUP BY collection_name
#  HAVING count >= 20
#  """
#
#  Group the collection names and addresses in groups amongst which they are statistically similar.
#  Explain the reasoning. Perform plots with plotly if needed. Make sure to return the resulting clustering in a table format, add the loan count, dollar volume
#  corresponding to that collection, as well as mean, median and standard deviation of the APR corresponding to that collection_name.
#  The capacity to explain and interpret the results is very important. Have a preference for simple data science tools like box plots with ranges,
#  rather than complex ones. Make sure that the chosen moment which is used for clustering, for instance the mean, makes sense e.g. that there are enough loans in that
#  collection_name sample or that the standard deviation is not too big.
# I would like five clusters, one for average APR in the 0% to 10% range, then 20% to 30%, 30% to 50%, 50% to 70%, then 80% and above.
#
#  Return the table containing the name, address of that collection, as well as the loan count, dollar volume, mean APR, median APR, standard deviation of APR and of course the cluster number to which it belongs to. In the legend of the plot, keep the cluster numbers from 1 to 5 ordered.
# from typing import Optional
#
# from google.cloud import bigquery
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import os
# import json
# import numpy as np
# from google.oauth2 import service_account
# import dotenv
# dotenv.load_dotenv()
#
# pd.set_option('print.max_columns', None)
# pd.set_option('print.max_rows', None)
# # pd.set_option('print.float_format', '{:,0f}'.format)
#
#
# def usd_to_str(usd_value, round_value: Optional[int] = None):
#     usd_str = f"$ {(round(usd_value, round_value) if not np.isnan(usd_value) else usd_value):,}".replace(',', "'")
#     return usd_str
#
#
# scopes = [
#     "https://www.googleapis.com/auth/drive",
#     "https://www.googleapis.com/auth/bigquery",
# ]


# def run_manual_clustering(grouping_key='mean', bucket_apr_ranges=[-0.1, 10, 20, 30, 40, 60]):
#     if os.environ.get("GCP_SERVICE_ACCOUNT", False):
#         credentials = service_account.Credentials.from_service_account_info(json.loads(os.environ["GCP_SERVICE_ACCOUNT"], strict=False)).with_scopes(scopes)
#         bigquery_client = bigquery.Client(credentials=credentials)
#     else:
#         # If deployed using App Engine, use default App Engine credentials
#         bigquery_client = bigquery.Client()
#
#     # Define query
#     query = """
#      SELECT collection_name, nft_collateral_contract as address, AVG(apr) as mean, APPROX_QUANTILES(apr, 2)[OFFSET(1)] as median, STDDEV(apr) as std, COUNT(*) as count, SUM(usd_value) as borrow_volume
#      FROM `nftfi_loan_data.nftfi_loan_data`
#      WHERE date >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)) AND apr <= 200
#      GROUP BY collection_name, address
#      HAVING count >= 20
#      """
#
#     # Execute query and convert results to pandas dataframe
#     df = bigquery_client.query(query).to_dataframe()
#     df.to_csv('analysis/raw_data.csv')
#
#     # Define clusters based on APR ranges
#     labels = range(1, len(bucket_apr_ranges))
#     df['cluster'] = pd.cut(df[grouping_key], bins=bucket_apr_ranges, labels=labels)
#
#     # Create table with name, address, loan count, dollar volume, mean APR, median APR, std APR, and cluster number
#     table = df[['collection_name', 'address', 'count', 'borrow_volume', 'mean', 'median', 'std', 'cluster']].sort_values(by=grouping_key)
#
#     sum_per_cluster_df = table.groupby('cluster').agg('sum')
#     sum_per_cluster_df = sum_per_cluster_df.rename(columns={'borrow_volume': 'borrow_volume_per_cluster', 'count': 'loan_count_per_cluster'})[['borrow_volume_per_cluster', 'loan_count_per_cluster']]
#     sum_per_cluster_df['cluster'] = sum_per_cluster_df.index
#     sum_per_cluster_df = sum_per_cluster_df.reset_index(drop=True)
#     table = pd.merge(left=table, right=sum_per_cluster_df, on='cluster')
#     table['borrow_volume_human_readable'] = table['borrow_volume'].apply(usd_to_str)
#     table['borrow_volume_per_cluster_human_readable'] = table['borrow_volume_per_cluster'].apply(usd_to_str)
#     print(table)
#
#     # Create box plot to visualize clusters
#     fig = px.box(df, x='cluster', y=grouping_key, color='cluster', labels={'cluster': 'Cluster Number', grouping_key: 'Mean APR'},
#                  category_orders={'cluster': labels}, hover_data=['collection_name', 'address', 'count', 'borrow_volume', grouping_key, 'median', 'std'])
#     fig.update_layout(title='Clustering of Collections based on Mean APR')
#
#     # Create scatter plot layer
#     scatter = go.Scatter(x=df['cluster'], y=df[grouping_key], mode='markers', text=df['collection_name'],
#                          marker=dict(color=df[grouping_key], colorscale='Viridis', opacity=0.7))
#
#     # Add scatter plot layer to box plot figure
#     fig.add_trace(scatter)
#     # Update x-axis label
#     fig.update_xaxes(title_text='Cluster Number')
#
#     # Update y-axis label
#     fig.update_yaxes(title_text='Mean APR')
#
#     fig.show()
#
#     scatter_fig = px.scatter(table, x=grouping_key, y='collection_name', color='cluster', hover_data=['address', 'collection_name'], size='borrow_volume')
#     scatter_fig.update_layout(title='Clustering of Collections based on Mean APR')
#     # Set the size of the figure and the background color
#     scatter_fig.update_layout(
#         autosize=False,
#         width=500,  # Set the width
#         height=500,  # Set the height
#         # plot_bgcolor='white',  # Set plot background color
#         paper_bgcolor='white',  # Set paper background color
#     )
#     scatter_fig.show()


from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
# pd.set_option('print.float_format', '{:,.2f}'.format)
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


def usd_to_str(usd_value, round_value: Optional[int] = None):
    usd_str = f"$ {(round(usd_value, round_value) if not np.isnan(usd_value) else usd_value):,}".replace(',', "'")
    return usd_str


def run_manual_clustering(grouping_key='mean', bucket_apr_ranges=[0, 10, 20, 30, 40, 60], include_unassigned_collections_to_last_bucket=True, autosize=False, save_table_as_csv=True):
    if include_unassigned_collections_to_last_bucket:
        bucket_apr_ranges[-1] = np.inf

    df = pd.read_csv('analysis/raw_data.csv')
    print(f"Number of collections in raw data: [{df.shape[0]}]")

    # Define clusters based on APR ranges
    labels = range(1, len(bucket_apr_ranges))
    df['cluster'] = pd.cut(df[grouping_key], bins=bucket_apr_ranges, labels=labels)

    # Create table with name, address, loan count, dollar volume, mean APR, median APR, std APR, and cluster number
    table = df[['collection_name', 'address', 'count', 'borrow_volume', 'mean', 'median', 'std', 'cluster']].sort_values(by=grouping_key)

    sum_per_cluster_df = table.groupby('cluster').agg('sum')
    sum_per_cluster_df = sum_per_cluster_df.rename(columns={'borrow_volume': 'borrow_volume_per_cluster', 'count': 'loan_count_per_cluster'})[['borrow_volume_per_cluster', 'loan_count_per_cluster']]
    sum_per_cluster_df['cluster'] = sum_per_cluster_df.index
    sum_per_cluster_df = sum_per_cluster_df.reset_index(drop=True)
    table = pd.merge(left=table, right=sum_per_cluster_df, on='cluster')
    nft_count_per_cluster_df = table.groupby('cluster').agg('count')
    nft_count_per_cluster_df = nft_count_per_cluster_df.rename(columns={'collection_name': 'nb_collection_per_cluster'})['nb_collection_per_cluster']
    table = pd.merge(left=table, right=nft_count_per_cluster_df, on='cluster')
    if save_table_as_csv:
        table.to_csv('nft_collection_apr_clusters.csv')

    print(table.head())

    # Create box plot to visualize clusters
    fig = px.box(df, x='cluster', y=grouping_key, color='cluster', labels={'cluster': 'Cluster Number', grouping_key: 'Mean APR'},
                 category_orders={'cluster': labels}, hover_data=['collection_name', 'address', 'count', 'borrow_volume', grouping_key, 'median', 'std'])
    fig.update_layout(title='Clustering of Collections based on Mean APR')
    if not autosize:
        fig.update_layout(
            width=1300,  # Set the width
            height=850,  # Set the height
        )
    fig.update_layout(paper_bgcolor='white')  # Set paper background color

    # Create scatter plot layer
    scatter = go.Scatter(x=df['cluster'], y=df[grouping_key], mode='markers', text=df['collection_name'],
                         marker=dict(color=df[grouping_key], colorscale='Viridis', opacity=0.7))

    # Add scatter plot layer to box plot figure
    fig.add_trace(scatter)
    # Update x-axis label
    fig.update_xaxes(title_text='Cluster Number')

    # Update y-axis label
    fig.update_yaxes(title_text='Mean APR')

    fig.show()

    scatter_fig = px.scatter(table, x=grouping_key, y='collection_name', color='cluster', hover_data=['address', 'collection_name'], size='borrow_volume')
    scatter_fig.update_layout(title='Clustering of Collections based on Mean APR')
    if not autosize:
        scatter_fig.update_layout(
            width=1200,  # Set the width
            height=600,  # Set the height
        )
    scatter_fig.update_layout(paper_bgcolor='white')  # Set paper background color
    scatter_fig.show()
    return table
