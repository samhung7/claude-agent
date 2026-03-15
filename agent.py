"""
Claude tool-use agent using the beta tool runner.

The tool runner handles the agentic loop automatically:
  - calls the API
  - detects tool_use requests
  - executes your tool functions
  - feeds results back to Claude
  - repeats until Claude stops calling tools
"""

import json
import math
import os
from datetime import datetime

import anthropic
from anthropic import beta_tool
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()
MODEL = "claude-opus-4-6"


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

@beta_tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the result.

    Args:
        expression: A Python math expression, e.g. "2 ** 10" or "math.sqrt(144)".
    """
    allowed = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)  # noqa: S307
        return str(result)
    except Exception as exc:
        return f"Error: {exc}"


@beta_tool
def get_current_time(timezone: str = "UTC") -> str:
    """Return the current date and time.

    Args:
        timezone: Timezone label to include in the response (informational only).
    """
    now = datetime.utcnow()
    return f"{now.strftime('%Y-%m-%d %H:%M:%S')} UTC (requested timezone: {timezone})"


@beta_tool
def search_knowledge_base(query: str, max_results: int = 3) -> str:
    """Search a local knowledge base and return relevant entries.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (1-10).
    """
    # Stub — replace with a real vector search, SQLite FTS, etc.
    knowledge = [
        {"title": "Python asyncio basics", "summary": "How to write async code with asyncio and await."},
        {"title": "REST API design", "summary": "Best practices for designing RESTful HTTP APIs."},
        {"title": "Claude tool use", "summary": "How to define and use tools with the Anthropic API."},
        {"title": "Docker networking", "summary": "Bridge, host, and overlay networks in Docker."},
        {"title": "SQL query optimization", "summary": "Index strategies and EXPLAIN output for slow queries."},
    ]
    results = [e for e in knowledge if query.lower() in e["title"].lower() or query.lower() in e["summary"].lower()]
    results = results[: max(1, min(max_results, 10))]
    if not results:
        return "No results found."
    return json.dumps(results, indent=2)


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------

TOOLS = [calculator, get_current_time, search_knowledge_base]

SYSTEM_PROMPT = """\
You are a helpful assistant with access to a calculator, a clock, and a knowledge base.
Use tools whenever they would give a more accurate or up-to-date answer.
Be concise.
"""


def run_agent(user_message: str) -> None:
    print(f"\nUser: {user_message}\n")

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=[{"role": "user", "content": user_message}],
    )

    for message in runner:
        for block in message.content:
            if block.type == "text" and block.text.strip():
                print(f"Claude: {block.text}")
            elif block.type == "thinking" and block.thinking.strip():
                print(f"[thinking] {block.thinking[:200]}{'...' if len(block.thinking) > 200 else ''}")
            elif block.type == "tool_use":
                print(f"[tool] {block.name}({json.dumps(block.input, ensure_ascii=False)})")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    examples = [
        "What is 2 to the power of 32?",
        "What time is it right now in Tokyo?",
        "What do you know about REST API design?",
        "Calculate the area of a circle with radius 7.5, then tell me the current time.",
    ]

    for prompt in examples:
        run_agent(prompt)
        print("-" * 60)
