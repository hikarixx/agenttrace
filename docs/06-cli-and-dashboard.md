# Chapter 6: CLI Command Reference & Dashboard Analytics

AgentTrace is engineered to deliver a flawless UI/UX experience across both spectrums of the engineering divide: For the hardcore terminal hackers, we provide an exquisite CLI/TUI. For product managers and executives, we deliver a stunning, Chart.js-powered Web Dashboard.

---

## 1. The Command Line Interface (CLI)

The AgentTrace CLI is constructed atop `Typer` and `Rich`. It abandons the dull, monochrome terminal outputs of the past, replacing them with vibrant color palettes, ascii trees, and pristine data tables.

### Quick Reference Command Matrix

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `agenttrace serve` | `--port 8000` | Initializes the FastAPI Backend Server and Web Dashboard. |
| `agenttrace top` | *(None)* | **[NEW]** Launches the `AgentTop` TUI (Terminal User Interface) to monitor runs in real-time, akin to the legendary `htop`. |
| `agenttrace runs` | `--limit 50` | Renders a color-coded terminal table displaying the 50 most recent execution sessions. |
| `agenttrace tree` | `<run_id>` | Prints the hierarchical execution tree in beautiful ASCII format (similar to the Linux `tree` command). |
| `agenttrace export-dataset`| `--output data.jsonl` | **[NEW]** Aggregates successful traces and exports them into an OpenAI-compatible JSONL dataset for 1-click model fine-tuning! |
| `agenttrace generate-tests`| `<run_id>` | **[NEW]** Analyzes tool inputs/outputs from a past run to autonomously generate a complete `pytest` suite mocking those identical interactions. |
| `agenttrace audit` | `<run_id>` | Scans the trace for security anomalies, calculates total USD costs, and generates a professional Markdown Audit Report. |

---

## 2. The Interactive Web Dashboard

The AgentTrace Web Dashboard is a blisteringly fast Single Page Application (SPA) utilizing Vanilla JavaScript and HTML. It requires zero Node.js dependencies and zero configuration.

### Dashboard Core Components

When you navigate to `http://localhost:8000`, you are presented with three primary data panels:

1. **The Session Ledger (Recent Runs)**
   - Smart ID Rendering: Only the first 8 characters are displayed to save screen real estate. Hovering via CSS tooltips reveals the full UUID.
   - Status Indicators: Visually coded as `completed` (Green), `failed` (Red), or `started` (Yellow).

2. **The Analytics Engine (Chart.js Visualization)**
   - AgentTrace has natively embedded **Chart.js**.
   - Upon selecting a Run, the Dashboard iterates through the Event Metadata. When it detects `prompt_tokens` and `completion_tokens`, it instantaneously renders a gorgeous **Stacked Bar Chart**. 
   - This provides executive-level visibility into exactly *which* tools and actions are consuming the most capital.

3. **Dual-Mode Event Log (Tree View & Chat View)**
   - **Tree View:** Displays a hierarchical, collapsible JSON tree. Ideal for deeply inspecting raw data payloads and system-level debugging.
   - **Chat View [NEW]:** A consumer-friendly, messenger-style interface. It filters for `user` and `agent` roles, rendering them as blue and white chat bubbles. This allows non-technical stakeholders to easily read and comprehend the conversational flow of the Agent.

---

[Next: Chapter 7 - Enterprise Security & Data Redaction →](07-security-and-redaction.md)
