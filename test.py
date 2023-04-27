# from analytics_bot_langchain.data.dune import run

# run()
import dotenv
import os

from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import Query


# foo = 'https://api.dune.com/api/v1/query/2419712/results?api_key=<api_key>'

dotenv.load_dotenv()
dune = DuneClient(os.environ["DUNE_API_KEY"])


def run(query_id=2419712):
    query = Query(
        name="Sample Query",
        query_id=query_id,
        # params=[
        #     QueryParameter.text_type(name="TextField", value="Word"),
        #     QueryParameter.number_type(name="NumberField", value=3.1415926535),
        #     QueryParameter.date_type(name="DateField", value="2022-05-04 00:00:00"),
        #     QueryParameter.enum_type(name="EnumField", value="Option 1"),
        # ],
    )
    print("Results available at", query.url())
    results = dune.refresh(query)
    return results

print(run())