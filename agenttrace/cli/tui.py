from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from ..storage.local import LocalStorage
import time
def start_tui():
    storage = LocalStorage()
    console = Console()
    def generate_layout() -> Layout:
        runs = storage.list_runs(limit=10)
        table = Table(title="Live AgentTrace Runs (Top 10)", expand=True, border_style="cyan")
        table.add_column("Run ID", style="dim", width=12)
        table.add_column("Agent", style="bold magenta")
        table.add_column("Status", justify="center")
        table.add_column("Started At", justify="right", style="green")
        active_count = 0
        total_runs = len(storage.list_runs(limit=1000))
        for r in runs:
            status_color = "[green]completed[/]" if r.status.value == "completed" else ("[red]failed[/]" if r.status.value == "failed" else "[yellow]started[/]")
            if r.status.value == "started": active_count += 1
            table.add_row(r.id[:8], r.agent, status_color, r.started_at.strftime("%H:%M:%S"))
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1)
        )
        header_text = f"AgentTrace TUI Monitor | Total Runs: {total_runs} | Active Now: {active_count} | Press Ctrl+C to exit"
        layout["header"].update(Panel(header_text, style="white on blue"))
        layout["main"].update(Panel(table, title="[b]Execution Log[/b]", border_style="blue"))
        return layout
    try:
        with Live(generate_layout(), refresh_per_second=2, screen=True):
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("[bold red]Exited AgentTrace TUI.[/bold red]")