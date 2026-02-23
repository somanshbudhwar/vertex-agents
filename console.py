"""
Interactive console for your deployed Vertex AI agent.

Requires deploy.py to have been run first (or set RESOURCE_NAME below manually).

  uv run python console.py

Commands:
  new     — start a fresh session (history is wiped server-side)
  history — print messages in the current session
  exit    — quit
"""

import os
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines

load_dotenv()

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
USER_ID = os.environ["USER_ID"]

# The root agent name — used to filter which events to display.
# Sub-agent (search_agent) events are shown as tool indicators, not full text.
ROOT_AGENT = "currency_and_search_exchange_agent"

vertexai.init(project=PROJECT, location=LOCATION)

# ── Load the deployed agent ────────────────────────────────────────────────────
# agent_engines.get() fetches the remote agent by its resource name.
# The agent lives on Vertex AI; this is just a lightweight client handle.
if os.path.exists(".resource_name"):
    resource_name = open(".resource_name").read().strip()
else:
    resource_name = input("Paste the agent resource name: ").strip()

print(f"Connecting to: {resource_name}")
remote = agent_engines.get(resource_name)

# ── Create a session ───────────────────────────────────────────────────────────
# Sessions are the core of Vertex AI's state management.
# Each session stores the full conversation history server-side,
# tied to a user_id. Later you'll add memory that persists *across* sessions.
session = remote.create_session(user_id=USER_ID)
session_id = session["id"]


def print_session_banner():
    print(f"\n{'─' * 52}")
    print(f"  Agent Console  |  user: {USER_ID}")
    print(f"  Session: {session_id}")
    print(f"{'─' * 52}")
    print("  Commands: 'new' · 'history' · 'exit'")
    print(f"{'─' * 52}\n")


def display_events(events):
    """
    ADK streams events for every step: tool calls, sub-agent calls, final text.
    We selectively display:
      - [tool: name]  when the agent calls a tool
      - final text    only from the root agent (not sub-agents)
    This gives you a window into what's happening under the hood.
    """
    print("Agent: ", end="", flush=True)
    for event in events:
        author = event.get("author", "")
        content = event.get("content") or {}
        parts = content.get("parts", [])

        for part in parts:
            if "function_call" in part:
                # The agent is invoking a tool or sub-agent
                name = part["function_call"].get("name", "")
                print(f"\n  ↳ [calling: {name}]", end="", flush=True)

            elif "text" in part and author == ROOT_AGENT:
                # Final text response from the root agent
                print(part["text"], end="", flush=True)

    print("\n")


def show_history():
    """
    Demonstrates Vertex AI's built-in session history retrieval.
    This is the conversation stored server-side — no local state needed.
    """
    history = remote.get_session(user_id=USER_ID, session_id=session_id)
    events = history.get("events", [])
    if not events:
        print("  (no messages yet)\n")
        return
    for e in events:
        author = e.get("author", "?")
        content = e.get("content") or {}
        for part in content.get("parts", []):
            if "text" in part:
                label = "You  " if author == "user" else "Agent"
                print(f"  {label}: {part['text']}")
    print()


# ── Main REPL ──────────────────────────────────────────────────────────────────
print_session_banner()

while True:
    try:
        user_input = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        break

    if not user_input:
        continue

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    if user_input.lower() == "new":
        session = remote.create_session(user_id=USER_ID)
        session_id = session["id"]
        print(f"\nNew session started: {session_id}\n")
        continue

    if user_input.lower() == "history":
        show_history()
        continue

    # stream_query sends the message to Vertex AI and streams back events.
    # The session_id ties this message to the ongoing conversation history.
    events = remote.stream_query(
        user_id=USER_ID,
        session_id=session_id,
        message=user_input,
    )
    display_events(events)
