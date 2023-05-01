
from datetime import datetime
import dotenv
import os
import pandas as pd

from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import Query
from dune_client.models import ExecutionState

from analytics_bot_langchain.data.bigquery_pipeline import Datatype

dotenv.load_dotenv()
dune = DuneClient(os.environ["DUNE_API_KEY"])

# Set the display options to show all columns and rows
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.expand_frame_repr", False)


def run(file_name: str, datatype: Datatype=Datatype.nftfi, query_id=2419712, time="1", frequency="HOUR", is_dex_data=False):
    params = []
    file_name = f"analytics_bot_langchain/data/dune/{datatype.value}/" + file_name
    if is_dex_data:
        file_name = f'dex_data_{time}_{frequency}_{datetime.now().strftime("%Y-%m-%d %H:%M").replace(" ", "_")}.csv'
        params = [
            QueryParameter.text_type(name="time", value=time),
            QueryParameter.text_type(name="frequency", value=frequency),
        ]
    query = Query(
        name="Sample Query",
        query_id=query_id,
        params=params,
    )
    print("Results available at", query.url())
    results = dune.refresh(query)
    # time.sleep(30)
    if results.state == ExecutionState.COMPLETED:
        df = pd.DataFrame(results.result.rows, columns=results.result.metadata.column_names)
        df.to_csv(f'{file_name}.csv', index=False)
    else:
        raise Exception(results.state)
    return df


