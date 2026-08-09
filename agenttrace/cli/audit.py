import json
from datetime import datetime
from agenttrace.storage.local import LocalStorage
def generate_audit_report(run_id: str, format: str = "md", output_file: str = None):
    storage = LocalStorage()
    try:
        data = storage.export_run(run_id)
    except Exception as e:
        print(f"Error loading run: {e}")
        return
    run = data["run"]
    events = data["events"]
    total_cost = 0.0
    tool_counts = {}
    dangerous_actions = []
    for event in events:
        meta = event.get("metadata", {})
        if "metrics" in meta and "estimated_cost_usd" in meta["metrics"]:
            total_cost += meta["metrics"]["estimated_cost_usd"]
        if event["type"] == "tool.started":
            tool_name = meta.get("tool_name", "unknown")
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        if event["status"] == "failed" and "Vi phạm Policy" in str(meta.get("error", "")):
            dangerous_actions.append(event)
        elif "decision" in meta and meta["decision"] == "deny":
            dangerous_actions.append(event)
    md = f"# AgentTrace Audit Report\n\n"
    md += f"**Run ID:** `{run['id']}`\n"
    md += f"**Agent:** {run['agent']}\n"
    md += f"**Task:** {run['task']}\n"
    md += f"**Status:** {run['status']}\n"
    md += f"**Duration:** {run['duration']}s\n"
    md += f"**Started At:** {run['started_at']}\n"
    md += f"**Total Cost:** ${total_cost:.5f}\n\n"
    md += f"## Tools Used\n"
    for tool, count in tool_counts.items():
        md += f"- **{tool}**: {count} times\n"
    md += f"\n## Security Alerts\n"
    if dangerous_actions:
        for action in dangerous_actions:
            md += f"- 🔴 **BLOCKED:** Tool `{action['metadata'].get('tool_name')}` at {action['timestamp']}\n"
            md += f"  - Reason: {action['metadata'].get('error', 'Denied by Policy')}\n"
    else:
        md += "✅ No security violations detected.\n"
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"Audit report saved to {output_file}")
    else:
        print(md)