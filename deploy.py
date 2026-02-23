"""
Deploy the agent to Vertex AI Agent Engine.

Run this ONCE. It uploads your agent to Google Cloud and saves the
resource name to .resource_name so console.py can find it.

  uv run python deploy.py
"""

import os
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines

from agent import root_agent

# .env is only used locally — the deployed agent on Vertex AI reads nothing from here.
# It just saves us from hardcoding values in source code.
load_dotenv()

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
STAGING_BUCKET = os.environ["STAGING_BUCKET"]

vertexai.init(project=PROJECT, location=LOCATION, staging_bucket=STAGING_BUCKET)

# Wrap the agent in an AdkApp — this is Vertex AI's container for ADK agents.
# It handles session routing, tool dispatch, and streaming for you.
app = agent_engines.AdkApp(agent=root_agent)

print("Deploying to Vertex AI Agent Engine... (this takes ~2-3 minutes)")
print("Vertex AI is packaging your code, uploading to GCS, and provisioning the endpoint.\n")

remote = agent_engines.create(
    app,
    requirements=[
        # These get pip-installed in the remote environment
        "google-cloud-aiplatform[adk,agent-engines]>=1.112",
        "requests",  # needed by get_exchange_rate
    ],
    # extra_packages uploads local .py files into the remote environment.
    # Without this, Vertex AI only sees deploy.py — not agent.py —
    # so `from agent import root_agent` fails with ModuleNotFoundError.
    extra_packages=["agent.py"],
    display_name="Currency and Search Agent",
    description="Handles currency exchange rates and internet search",
)

print(f"\n✅ Agent deployed successfully!")
print(f"Resource name: {remote.resource_name}")
print(f"\nYou can view it in the Cloud Console:")
print(f"https://console.cloud.google.com/vertex-ai/agents?project={PROJECT}")

# Save so console.py can pick it up automatically
with open(".resource_name", "w") as f:
    f.write(remote.resource_name)
print("\nResource name saved to .resource_name — run console.py next.")
