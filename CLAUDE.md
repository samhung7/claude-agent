# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your ANTHROPIC_API_KEY
```

## Running

```bash
python agent.py
```

## Architecture

Single-file agent (`agent.py`) built on the Anthropic Python SDK beta tool runner.

**Key design decisions:**

- Tools are decorated with `@beta_tool` — schemas are auto-generated from type hints and docstrings. No manual JSON schema needed.
- The `tool_runner()` call handles the full agentic loop (API call → tool execution → feed results back → repeat) automatically. Do not reimplement the loop manually unless you need fine-grained control (custom logging, human-in-the-loop approval, etc.).
- Model: `claude-opus-4-6` with `thinking: {"type": "adaptive"}` (the recommended approach — do **not** use `budget_tokens`, which is deprecated on Opus 4.6).
- `TOOLS` list is the single source of truth for available tools. Add new tools there.

**Adding a new tool:**

```python
@beta_tool
def my_tool(param: str) -> str:
    """One-line description used by Claude to decide when to call this tool.

    Args:
        param: Description of this parameter.
    """
    return "result"

TOOLS = [..., my_tool]
```

**Replacing the knowledge base stub:** `search_knowledge_base` in `agent.py` is a placeholder. Swap the `knowledge` list for a real vector search (e.g., `chromadb`, `pgvector`) or SQLite FTS query.
