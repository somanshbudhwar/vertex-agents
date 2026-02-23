import requests
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool


def get_exchange_rate(
    currency_from: str = "USD",
    currency_to: str = "EUR",
    currency_date: str = "latest",
):
    """Retrieves the exchange rate between two currencies on a specified date."""
    response = requests.get(
        f"https://api.frankfurter.app/{currency_date}",
        params={"from": currency_from, "to": currency_to},
    )
    return response.json()


_search_agent = Agent(
    model="gemini-2.5-flash",
    name="search_agent",
    instruction="You are a web search assistant. Use google_search to answer questions about current events and news.",
    tools=[google_search],
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="currency_and_search_exchange_agent",
    instruction="""
        You are a helpful assistant. Use your tools when the user asks for:
        - Current news and information  → delegate to search_agent_tool
        - Currency exchange rates       → use get_exchange_rate

        Always cite which tool you used and summarise the result clearly.
    """,
    tools=[get_exchange_rate, AgentTool(agent=_search_agent)],
)
