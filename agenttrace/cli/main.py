import typer
import json
import uvicorn
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from ..storage.local import LocalStorage
app = typer.Typer(help="AgentTrace CLI - Record, store, and visualize AI Agent execution")
console = Console()
storage = LocalStorage()
@app.command()
def runs(limit: int = 100):
    runs = storage.list_runs(limit=limit)
    if not runs:
        console.print("No runs found.")
        return
    table = Table("ID", "Agent", "Task", "Status", "Duration (s)", "Started At")
    for r in runs:
        duration_str = f"{r.duration:.2f}" if r.duration is not None else "N/A"
        table.add_row(r.id[:8], r.agent, r.task, r.status.value, duration_str, r.started_at.strftime("%Y-%m-%d %H:%M:%S"))
    console.print(table)
@app.command()
def show(run_id: str):
    run = storage.get_run(run_id)
    if not run:
        runs = storage.list_runs()
        matches = [r for r in runs if r.id.startswith(run_id)]
        if len(matches) == 1:
            run = matches[0]
        else:
            console.print(f"[red]Run {run_id} not found[/red]")
            return
    console.print(f"[bold]Run ID:[/bold] {run.id}")
    console.print(f"[bold]Agent:[/bold] {run.agent}")
    console.print(f"[bold]Task:[/bold] {run.task}")
    console.print(f"[bold]Status:[/bold] {run.status.value}")
    console.print(f"[bold]Duration:[/bold] {run.duration:.2f}s" if run.duration else "[bold]Duration:[/bold] N/A")
    console.print(f"[bold]Started:[/bold] {run.started_at}")
    console.print(f"[bold]Metadata:[/bold] {json.dumps(run.metadata, indent=2)}")
@app.command()
def events(run_id: str):
    run = storage.get_run(run_id)
    if not run:
        runs = storage.list_runs()
        matches = [r for r in runs if r.id.startswith(run_id)]
        if len(matches) == 1:
            run_id = matches[0].id
        else:
            console.print(f"[red]Run {run_id} not found[/red]")
            return
    events = storage.get_events(run_id)
    if not events:
        console.print("No events found.")
        return
    table = Table("Time", "Type", "Status", "Duration (s)", "Tool")
    for e in events:
        duration_str = f"{e.duration:.2f}" if e.duration is not None else "N/A"
        tool_name = e.metadata.get("tool_name", "")
        table.add_row(e.timestamp.strftime("%H:%M:%S"), e.type.value, e.status.value, duration_str, tool_name)
    console.print(table)
@app.command()
def tree(run_id: str):
    run = storage.get_run(run_id)
    if not run:
        runs = storage.list_runs()
        matches = [r for r in runs if r.id.startswith(run_id)]
        if len(matches) == 1:
            run_id = matches[0].id
        else:
            console.print(f"[red]Run {run_id} not found[/red]")
            return
    try:
        data = storage.export_run(run_id)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        return
    def print_node(node, level=0):
        indent = "  " * level
        tool = f" [{node['metadata'].get('tool_name')}]" if 'tool_name' in node['metadata'] else ""
        console.print(f"{indent}- {node['type']} ({node['status']}){tool}")
        for child in node.get("children", []):
            print_node(child, level + 1)
    for root in data["tree"]:
        print_node(root)
@app.command()
def export(run_id: str, output: str = None):
    run = storage.get_run(run_id)
    if not run:
        runs = storage.list_runs()
        matches = [r for r in runs if r.id.startswith(run_id)]
        if len(matches) == 1:
            run_id = matches[0].id
        else:
            console.print(f"[red]Run {run_id} not found[/red]")
            return
    try:
        data = storage.export_run(run_id)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        return
    json_str = json.dumps(data, indent=2)
    if output:
        with open(output, "w") as f:
            f.write(json_str)
        console.print(f"Exported to {output}")
    else:
        print(json_str)
@app.command()
def delete(run_id: str):
    run = storage.get_run(run_id)
    if not run:
        runs = storage.list_runs()
        matches = [r for r in runs if r.id.startswith(run_id)]
        if len(matches) == 1:
            run_id = matches[0].id
        else:
            console.print(f"[red]Run {run_id} not found[/red]")
            return
    storage.delete_run(run_id)
    console.print(f"Run {run_id} deleted.")
@app.command()
def audit(run_id: str, format: str = "md", output: str = None):
    from .audit import generate_audit_report
    run = storage.get_run(run_id)
    if not run:
        runs = storage.list_runs()
        matches = [r for r in runs if r.id.startswith(run_id)]
        if len(matches) == 1:
            run_id = matches[0].id
        else:
            console.print(f"[red]Run {run_id} not found[/red]")
            return
    generate_audit_report(run_id, format, output)
@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def mcp_proxy(ctx: typer.Context):
    if not ctx.args:
        console.print("[red]Lỗi: Cần cung cấp lệnh chạy MCP Server. Ví dụ: agenttrace mcp-proxy -- npx -y @modelcontextprotocol/server-everything[/red]")
        return
    command = ctx.args
    if command[0] == "--":
        command = command[1:]
    from .adapters.mcp_proxy import MCPProxy
    proxy = MCPProxy(command)
    proxy.start()
@app.command()
def top():
    from .tui import start_tui
    start_tui()
@app.command()
def export_dataset(output: str = "dataset.jsonl"):
    from .export_dataset import export_openai_dataset
    export_openai_dataset(output)
@app.command()
def generate_tests(run_id: str, output: str = "test_agent.py"):
    from .generate_tests import generate_pytest_file
    run = storage.get_run(run_id)
    if not run:
        runs = storage.list_runs()
        matches = [r for r in runs if r.id.startswith(run_id)]
        if len(matches) == 1:
            run_id = matches[0].id
        else:
            console.print(f"[red]Run {run_id} not found[/red]")
            return
    generate_pytest_file(run_id, output)
@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000):
    console.print(f"Starting AgentTrace Dashboard on http://{host}:{port}")
    uvicorn.run("agenttrace.server.api:app", host=host, port=port, reload=False)
if __name__ == "__main__":
    app()