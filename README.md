# DevPulse

> MCP + ReAct Agent + LangGraph Multi-Agent + A2A Agent Card — all wired to the live GitHub REST API.

DevPulse is a progressive, five-phase capstone reference implementation that demonstrates how modern AI-agent protocols fit together. Every tool call hits `api.github.com` for real — no mocks, no canned data.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Phase 1 — MCP Protocol Test](#phase-1--mcp-protocol-test)
  - [Phase 2 — Model Connection Check](#phase-2--model-connection-check)
  - [Phase 3 — Single ReAct Agent](#phase-3--single-react-agent-human-in-the-loop)
  - [Phase 4 — LangGraph Multi-Agent](#phase-4--langgraph-multi-agent)
  - [Phase 5 — A2A Agent Card](#phase-5--a2a-agent-card)
- [MCP Tools Reference](#mcp-tools-reference)
- [How It Works](#how-it-works)
- [Engineering Notes](#engineering-notes)
- [License](#license)

---

## Overview

DevPulse ties together four key AI-agent concepts into one working system:

| Concept | What It Solves | DevPulse Implementation |
|---------|---------------|------------------------|
| **MCP (Model Context Protocol)** | Agent-to-tool access | `mcp_server.py` exposes GitHub data as tools, resources, and prompts |
| **ReAct Agent** | Reasoning + action loop | `agent_core.py` implements a single-loop agent with memory and human approval |
| **LangGraph** | Multi-agent orchestration | `langgraph_agent.py` routes queries to scoped specialist nodes |
| **A2A (Agent-to-Agent)** | Agent discovery | `a2a_card.py` publishes capabilities via a discoverable Agent Card |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     A2A Agent Card                                │
│                (a2a_card.py) — Phase 5                            │
│           External agent discovery via skills                     │
├──────────────────────────────────────────────────────────────────┤
│                  LangGraph Multi-Agent                            │
│             (langgraph_agent.py) — Phase 4                        │
│      Router → {Repo Analyst, Issue Triage, Releases}              │
├──────────────────────────────────────────────────────────────────┤
│                  Single ReAct Agent                               │
│              (agent_core.py) — Phase 3                            │
│       Model + Tools + Memory + Human-in-the-Loop                  │
├──────────────────────────────────────────────────────────────────┤
│           Shared Infrastructure — Phase 2                         │
│    model_client.py (LLM connector)                                │
│    mcp_bridge.py (MCP → OpenAI tool bridge)                       │
├──────────────────────────────────────────────────────────────────┤
│           MCP Server + Protocol Test — Phase 1                    │
│    mcp_server.py (5 tools, 1 resource, 1 prompt)                  │
│    mcp_client_test.py (initialize → list → call)                  │
├──────────────────────────────────────────────────────────────────┤
│                  GitHub REST API                                   │
│                api.github.com (live)                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
DevPulse/
├── mcp_server.py          # Phase 1 — MCP server with GitHub tools
├── mcp_client_test.py     # Phase 1 — Protocol-level test (no LLM)
├── model_client.py        # Phase 2 — Backend-agnostic LLM connector
├── mcp_bridge.py          # Phase 2 — MCP schema → OpenAI function-calling bridge
├── agent_core.py          # Phase 3 — Single ReAct agent with HITL
├── langgraph_agent.py     # Phase 4 — LangGraph multi-agent router
├── a2a_card.py            # Phase 5 — A2A Agent Card + registry
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
└── README.md              # This file
```

---

## Prerequisites

- **Python 3.10+**
- An LLM backend (one of the following):
  - **OpenAI** API key (default)
  - **Groq** API key (free tier available)
  - **Ollama** running locally (free, no API key)
- A **GitHub Personal Access Token** (optional, but recommended — raises rate limit from 60 to 5,000 requests/hour)

---

## Setup

```bash
# Clone the repository
git clone git@github.com:a-fham/DevPulse.git
cd DevPulse

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your environment file
cp .env.example .env
```

Edit `.env` with your credentials (see [Configuration](#configuration) below).

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
# ── LLM Backend ──────────────────────────────────
LLM_BACKEND=openai          # "openai", "groq", or "ollama"

# ── OpenAI (default) ─────────────────────────────
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# ── Groq (cloud, free tier) ──────────────────────
# GROQ_API_KEY=gsk_...
# GROQ_MODEL=llama-3.1-8b-instant

# ── Ollama (local) ──────────────────────────────
# OLLAMA_BASE_URL=http://localhost:11434/v1
# OLLAMA_MODEL=qwen2.5:3b

# ── GitHub ───────────────────────────────────────
# Optional but recommended — raises rate limit
# GITHUB_TOKEN=ghp_...
```

### Backend Comparison

| Backend | API Key | Cost | Latency | Model |
|---------|---------|------|---------|-------|
| OpenAI | Required | Pay-per-token | ~1-3s | `gpt-4o-mini` |
| Groq | Required (free) | Free tier available | ~0.5-1s | `llama-3.1-8b-instant` |
| Ollama | Not required | Free | ~2-5s | `qwen2.5:3b` (configurable) |

---

## Usage

### Phase 1 — MCP Protocol Test

Validates the MCP server works end-to-end without any LLM involvement.

```bash
python mcp_client_test.py
```

**What happens:**
1. Launches `mcp_server.py` as a subprocess
2. Initializes the MCP session (protocol handshake)
3. Discovers all tools, resources, and prompts
4. Executes a real `search_repositories` call to the GitHub API
5. Prints the results

---

### Phase 2 — Model Connection Check

Verifies your LLM backend is reachable and configured correctly.

```bash
python -c "from dotenv import load_dotenv; load_dotenv(); from model_client import get_client_and_model, check_connection; c,m,b=get_client_and_model(); check_connection(c,m,b)"
```

---

### Phase 3 — Single ReAct Agent (Human-in-the-Loop)

An interactive chat agent that reasons, selects tools, and asks for your approval before each tool execution.

```bash
python agent_core.py
```

**Example session:**

```
You: tell me about facebook/react
→ Agent wants to call: get_repo_details(owner="facebook", repo="react")
→ Approve? (y/n): y
→ Stars: 234k, Forks: 48k, License: MIT

You: now show me its top contributors
→ Agent wants to call: list_contributors(owner="facebook", repo="react", limit=5)
→ Approve? (y/n): y
→ 1. sebmarkbage (1,204 commits) ...
```

**Key features:**
- Conversational memory across turns
- Human-in-the-loop approval for every tool call
- Automatic retry if denied
- Capped at 4 reasoning loops per query

---

### Phase 4 — LangGraph Multi-Agent

A router classifies your query and dispatches it to a specialist agent with scoped tool access.

```bash
python langgraph_agent.py
```

**Example session:**

```
You: what are the open issues on facebook/react?
→ Routed to: issue_triage
→ 12,430 open issues. Top labels: Status: Unconfirmed, Type: Bug ...

You: what's the latest release of nextcloud/server?
→ Routed to: release_notes
→ Latest: v30.0.0 — "Nextcloud Hub 9 includes ..."
```

**Specialist routing:**

| Query Type | Specialist | Allowed Tools |
|-----------|-----------|---------------|
| Repo info, search, contributors | `repo_info` | `search_repositories`, `get_repo_details`, `list_contributors` |
| Issues, bugs, triage | `issue_triage` | `list_open_issues` |
| Releases, versions, changelogs | `release_notes` | `get_latest_release` |

---

### Phase 5 — A2A Agent Card

Demonstrates how DevPulse publishes itself as a discoverable Agent Card for external agent-to-agent discovery.

```bash
python a2a_card.py
```

**Output:**

```
Registered agent: DevPulse
  Skills: repo_info, issue_triage, release_notes

Discovery by tag "github":
  → DevPulse (skills: repo_info, issue_triage, release_notes)
```

---

## MCP Tools Reference

The MCP server exposes five tools to the GitHub REST API:

| Tool | Parameters | Description |
|------|-----------|-------------|
| `search_repositories` | `query` | Search repos by keyword, topic, or language, sorted by stars |
| `get_repo_details` | `owner`, `repo` | Get stars, forks, license, description |
| `list_open_issues` | `owner`, `repo`, `limit=10` | List open issues with labels |
| `list_contributors` | `owner`, `repo`, `limit=10` | Top contributors by commit count |
| `get_latest_release` | `owner`, `repo` | Latest release tag and notes |

**Resources:**

| URI | Description |
|-----|-------------|
| `github://repo/{owner}/{repo}/summary` | Pre-formatted repository snapshot |

**Prompts:**

| Prompt | Description |
|--------|-------------|
| `issue_triage_prompt` | Structured workflow for issue classification |

---

## How It Works

### MCP Server

Built with FastMCP. Each tool function makes live HTTP calls to `api.github.com` via `httpx`. The server runs as a subprocess communicating over stdin/stdout using MCP's JSON-RPC protocol.

### MCP Bridge

Dynamically converts MCP tool schemas into OpenAI function-calling format at runtime. No hard-coded schemas — the tool list always reflects the live MCP server.

### Model Client

A factory function (`get_client_and_model()`) returns a backend-agnostic client. All three backends (OpenAI, Groq, Ollama) expose the same `client.chat.completions.create()` interface.

### ReAct Agent

Implements the loop: **Reason → Select Tool → Human Approval → Execute → Observe → Repeat**. Maintains conversation history across turns.

### LangGraph Multi-Agent

Uses `StateGraph` with conditional edges. A router classifies the query, then dispatches to one of three scoped specialist nodes. Each specialist only has access to its relevant tools.

### A2A Agent Card

Defines capabilities as a Pydantic `AgentCard` with tagged skills. An `AgentRegistry` enables tag-based discovery — external agents see only the card, not the implementation details.

---

## Engineering Notes

- **stdout vs stderr discipline** — MCP's JSON-RPC protocol owns stdout; all server logging goes to stderr
- **Environment inheritance** — `StdioServerParameters` doesn't inherit parent env by default; use `env=os.environ.copy()`
- **Rate limiting** — Unauthenticated GitHub requests are capped at 60/hour; set `GITHUB_TOKEN` for 5,000/hour
- **MCP vs A2A boundary** — MCP solves agent-to-tool access; A2A solves agent-to-agent discovery

---

## License

This project is for educational and demonstration purposes.
