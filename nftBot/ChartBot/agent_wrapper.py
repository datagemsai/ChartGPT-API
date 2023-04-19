

from dotenv import load_dotenv
from slack_bot.agents.routing_sql_agent import routing_agent

# Load environment variables from the .env file
load_dotenv()

routing_agent = routing_agent()
agent = routing_agent


def get_agent():
    return agent

