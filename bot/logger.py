import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.table import Table
from datetime import datetime

console = Console()

class BotLogger:
    def __init__(self):
        self.log = logging.getLogger("YouTubeBot")
        self.log.setLevel(logging.INFO)
        
        handler = RichHandler(
            rich_tracebacks=True,
            console=console,
            show_time=True,
            show_path=False
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.log.addHandler(handler)

    def info(self, msg):
        self.log.info(f"[bold cyan]ℹ[/] {msg}")
    
    def success(self, msg):
        self.log.info(f"[bold green]✓[/] {msg}")
    
    def warning(self, msg):
        self.log.warning(f"[bold yellow]⚠[/] {msg}")
    
    def error(self, msg):
        self.log.error(f"[bold red]✗[/] {msg}")
    
    def progress_table(self, current, total, url, duration, elapsed):
        """Tampilkan progress di tengah interface"""
        table = Table(show_header=False, box=None, padding=0)
        table.add_column("Status", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("🎯 Target", url[:50] + ("..." if len(url) > 50 else ""))
        table.add_row("📊 Progress", f"[bold yellow]{current}/{total}[/]")
        table.add_row("⏱ Durasi", f"{elapsed}/{duration}s")
        table.add_row("🕒 Waktu", datetime.now().strftime("%H:%M:%S"))
        console.print(table)