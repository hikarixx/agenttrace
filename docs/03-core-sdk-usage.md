# Chapter 3: Core SDK Programming Guide

The Core SDK is the beating heart of AgentTrace. If you are building a proprietary AI Agent entirely from scratch using standard Python (eschewing frameworks like LangChain or LlamaIndex), this is where your journey begins.

---

## 1. Initializing the Tracer & Storage Configuration

Before capturing events, you must initialize the `Tracer` engine. AgentTrace is flexible, allowing you to persist data locally during development or stream it to an Enterprise PostgreSQL cluster in production.

```python
from agenttrace.core import Tracer
from agenttrace.storage.postgres import PostgresStorage

# Option 1: SQLite for rapid local development (Default)
tracer_local = Tracer(db_path="local_logs.db")

# Option 2: Enterprise PostgreSQL for distributed production workloads
pg_storage = PostgresStorage("postgresql://user:pass@localhost/agentdb")
tracer_pg = Tracer(storage=pg_storage)
```

---

## 2. Managing the Execution Lifecycle

In the AgentTrace ecosystem, a complete user interaction or specific task goal is encapsulated within a `Run`.

```python
# 1. Initialize a new Run
run_id = tracer_local.start_run(
    agent="ProprietaryFinancialAgent", 
    task="Analyze Q3 SEC filings for Apple Inc."
)

# 2. CRITICAL: Bind the Run ID to the execution context
# This utilizes ContextVars to ensure thread-safe tracing. 
# Subsequent decorators will automatically resolve this Run ID.
tracer_local.set_current_run(run_id)

try:
    # ... Execute your complex AI logic here ...
    pass
except Exception as e:
    # 3. Explicitly fail the run upon catastrophic errors
    tracer_local.end_run(run_id, status="failed")
    raise e
finally:
    # 4. Guarantee Run closure
    tracer_local.end_run(run_id, status="completed")
```

---

## 3. The Power of Decorators: Tracing Tool Invocations

Manually crafting JSON event payloads is tedious. AgentTrace provides two elegant decorators: `@trace_tool` (for synchronous execution) and `@async_trace_tool` (for high-performance asynchronous execution).

### A. Synchronous Execution

```python
from agenttrace.core import trace_tool

@trace_tool
def fetch_weather(city: str):
    """A tool enabling the LLM to retrieve current meteorological data."""
    import requests
    res = requests.get(f"https://wttr.in/{city}?format=j1")
    return res.json()

# Simply invoke the function normally. 
# AgentTrace silently intercepts the Input ("London") and the resulting JSON Output,
# securely logging the transaction into your database.
fetch_weather("London")
```

### B. Asynchronous Execution (High-Performance Applications)

> [!TIP]
> When architecting production-grade applications, network bound operations (such as querying OpenAI APIs or scraping web pages) should **ALWAYS** utilize asynchronous paradigms (`asyncio`) to prevent thread-blocking bottlenecks.

```python
import asyncio
from agenttrace.core.async_tracer import AsyncTracer, async_trace_tool

async_tracer = AsyncTracer(db_path="async_logs.db")
async_tracer.set_current_run(run_id)

@async_trace_tool
async def download_dataset_async(url: str):
    await asyncio.sleep(1) # Simulating I/O latency
    return f"Successfully downloaded 100MB chunk from {url}"

# AgentTrace strictly awaits the resolution of the coroutine before writing the event.
await download_dataset_async("https://enterprise-bucket.s3.amazonaws.com/data.csv")
```

---

## 4. Unparalleled Exception Handling

The true power of the `@trace_tool` architecture lies in its exception resilience. Should your tool encounter a fatal error (e.g., network timeout, zero division, database disconnect), AgentTrace automatically catches the exception, captures the entire Stack Trace, logs the event with a `FAILED` status, and gracefully re-raises the exception back to your application flow.

Consequently, when investigating issues within the Web Dashboard, failing tool calls are vividly highlighted in **Red**, providing immediate visibility into precisely *why* the Agent's reasoning loop collapsed.

---

[Next: Chapter 4 - Multi-Agent Frameworks & Adapters →](04-adapters-integration.md)
