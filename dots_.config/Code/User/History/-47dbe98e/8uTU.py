#!/usr/bin/env python3
import subprocess, re, argparse
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import MINIMAL_HEAVY_HEAD

def parse_last_output():
    # last -x çıktısını al
    result = subprocess.run(["last", "-x"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")

    parsed_entries = []
    year = datetime.now().year

    for line in lines:
        if not line.startswith("reboot"):
            continue  # sadece reboot satırlarını işle

        match = re.match(
            r"(?P<type>reboot)\s+system boot\s+(?P<kernel>[\w\.\-\*]+)?\s+(?P<start>\w{3}\s+\w{3}\s+\d+\s+\d+:\d+)"
            r"(?:\s+-\s+(?P<end>\w{3}\s+\d+:\d+|\d+:\d+|crash|down|still running))?\s+\((?P<duration>[^)]+)\)",
            line
        )

        if not match:
            continue

        # Tarihi parse ederken yıl ekleyerek DeprecationWarning'i engelle
        start_str = match.group("start")
        try:
            start_dt = datetime.strptime(f"{year} {start_str}", "%Y %a %b %d %H:%M")
        except ValueError:
            continue  # hatalı tarih varsa atla

        parsed_entries.append({
            "type": match.group("type"),
            "kernel": match.group("kernel") or "-",
            "start_dt": start_dt,
            "duration": match.group("duration"),
            "end": match.group("end") or "still running"
        })

    # Zamana göre ters sırala (en yeni üstte)
    parsed_entries.sort(key=lambda x: x["start_dt"], reverse=True)
    return parsed_entries

def format_duration(duration_str):
    if duration_str.strip() == "00:00":
        return "a few sec"

    if "+" in duration_str:
        days_part, time_part = duration_str.split("+")
        days = int(days_part.strip())
        hours, minutes = map(int, time_part.strip().split(":"))
        return f"{days}d {hours}h {minutes}m"
    else:
        hours, minutes = map(int, duration_str.strip().split(":"))
        return f"{hours}h {minutes}m"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show boot history with optional date format.")
    parser.add_argument("--long-date", action="store_true", help="Display date as 'May 05, 2025' instead of '2025-05-05'")
    args = parser.parse_args()

    entries = parse_last_output()
    use_long_date = args.long_date
    console = Console()

    #table = Table(title="Boot Sessions", show_lines=True)
    table = Table(
        box=MINIMAL_HEAVY_HEAD,
        show_lines=False
        #expand=True
    )

    #table.add_column("#", justify="right", style="cyan", no_wrap=True)
    #table.add_column("Boot Time", style="magenta")
    #table.add_column("Shutdown", style="magenta")
    #table.add_column("Uptime", style="green")
    #table.add_column("Exit", style="red")
    #table.add_column("Kernel", style="yellow")
    
    table.add_column("Boot Time", style="bright_cyan", no_wrap=True, justify="left")  # solda kalmalı
    table.add_column("Shutdown", style="bright_magenta", no_wrap=True, justify="left")  # solda kalmalı
    table.add_column("Uptime", style="green", justify="center")  # orta
    table.add_column("Exit", justify="center")  # ortalanabilir, sağ da olabilir
    table.add_column("Kernel", style="yellow", justify="right")  # sağa yasla

    for i, entry in enumerate(entries, 1):
        # Uptime'ı gün+saat olarak çöz
        days = 0
        hours, minutes = 0, 0
        duration = entry["duration"]

        if "+" in duration:
            days_part, time_part = duration.split("+")
            days = int(days_part.strip())
            hours, minutes = map(int, time_part.strip().split(":"))
        else:
            hours, minutes = map(int, duration.strip().split(":"))
        
        shutdown_dt = entry["start_dt"] + timedelta(days=days, hours=hours, minutes=minutes)
        shutdown = shutdown_dt.strftime("%Y-%m-%d %H:%M")

        if use_long_date:
            boot_time = entry["start_dt"].strftime("%b %d, %Y %H:%M")  # May 05, 2025 22:27
            shutdown = shutdown_dt.strftime("%b %d, %Y %H:%M")
        else:
            boot_time = entry["start_dt"].strftime("%Y-%m-%d %H:%M")  # 2025-05-05 22:27
            shutdown = shutdown_dt.strftime("%Y-%m-%d %H:%M")

        # Eğer end 'crash' ya da 'down' ise exit_type'ı ona göre yaz
        if entry["end"] == "crash":
            exit_type = "crash"
        elif entry["end"] == "still running":
            shutdown = "still running"
            exit_type = "running"
        else:
            exit_type = "shutdown"

        from rich.text import Text

        exit_text = Text(exit_type)
        if exit_type == "crash":
            exit_text.stylize("bold red")
        elif exit_type == "shutdown":
            exit_text.stylize("bright_green")
        elif exit_type == "running":
            exit_text.stylize("yellow")

        table.add_row(
            boot_time,
            shutdown,
            format_duration(entry["duration"]),
            exit_text,
            entry["kernel"]
        )


    #console.print(table)
    console.print(Panel(table, title="Boot History", border_style="cyan", padding=(0, 1), expand=False))

