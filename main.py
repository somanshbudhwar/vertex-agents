import vertexai
from vertexai import agent_engines
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

client = vertexai.Client(
project="agentic-ai-488117", location="us-central1",)

def get_exchange_rate(
    currency_from: str = "USD",
    currency_to: str = "EUR",
    currency_date: str = "latest",
):
    """Retrieves the exchange rate between two currencies on a specified date."""
    import requests

    response = requests.get(
        f"https://api.frankfurter.app/{currency_date}",
        params={"from": currency_from, "to": currency_to},
    )
    return response.json()


from google.adk.agents import Agent
from vertexai import agent_engines

search_agent = Agent(
    model="gemini-2.5-flash",
    name="search_agent",
    instruction="You are a web search assistant. Use google_search to answer questions about current events and news.",
    tools=[google_search],
)

search_agent_tool = AgentTool(agent=search_agent)

agent = Agent(
    model="gemini-2.5-flash",
    name='currency_and_search_exchange_agent',
    instruction="""
        You are a helpful assistant. Use your tools when the user asks for:
        - Current news and information  → delegate to search_agent_tool
        - Currency exchange rate   → use get_exchange_rate

        Always cite which tool you used and summarise the result clearly.
    """,
    tools=[get_exchange_rate,search_agent_tool],
)

app = agent_engines.AdkApp(agent=agent)

import asyncio

async def main():
    async for event in app.async_stream_query(
        user_id="somansh",
        message="What is the winter olympics news today?",
    ):
        print(event)

if __name__ == "__main__":
    asyncio.run(main())
