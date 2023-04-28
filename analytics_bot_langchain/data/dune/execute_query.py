
from datetime import datetime
import dotenv
import os
import pandas as pd

from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import Query
from dune_client.models import ExecutionState

dotenv.load_dotenv()
dune = DuneClient(os.environ["DUNE_API_KEY"])

# Set the display options to show all columns and rows
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.expand_frame_repr", False)

def run(query_id=2419712, time="1", frequency="HOUR"):
    query = Query(
        name="Sample Query",
        query_id=query_id,
        params=[
            QueryParameter.text_type(name="time", value=time),
            QueryParameter.text_type(name="frequency", value=frequency),
        ],
    )
    print("Results available at", query.url())
    results = dune.refresh(query)
    # time.sleep(30)
    if results.state == ExecutionState.COMPLETED:
        df = pd.DataFrame(results.result.rows, columns=results.result.metadata.column_names)
        df.to_csv(f'dex_data_{time}_{frequency}_{datetime.now().strftime("%Y-%m-%d %H:%M").replace(" ", "_")}.csv', index=False)
    else:
        raise Exception(results.state)
    return df

print(run(2421110))
