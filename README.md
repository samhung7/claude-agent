# Claude Agent

A Python tool-use agent built on the [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) beta tool runner.

## Features

- **Calculator** — evaluates math expressions using Python's `math` module
- **Clock** — returns the current UTC time
- **Knowledge base** — searches a local stub (swap in a real vector DB)
- Adaptive thinking (`claude-opus-4-6`)
- Parallel tool calls — Claude batches independent tools automatically

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
```

## Run

```bash
python3 agent.py
```

## Adding a Tool

```python
@beta_tool
def my_tool(param: str) -> str:
    """Description Claude uses to decide when to call this tool.

    Args:
        param: What this parameter does.
    """
    return "result"

TOOLS = [..., my_tool]
```

Schemas are generated automatically from type hints and docstrings — no manual JSON required.
