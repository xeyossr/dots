#!/usr/bin/env python3
import subprocess
import re
import argparse
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import MINIMAL_HEAVY_HEAD
from rich.text import Text

def parse_last_output():
    """Parse 'last -x' output to extract system boot entries, including 'still running'."""
    output = subprocess.check_output(["last", "-x"], text=True)
    lines = output.strip().split("\n")

    parsed_entries = []
    year = datetime.now().year

    # Regex updated to allow duration to be optional
    RE_BOOT_LINE = re.compile(
        r"(?P<type>reboot)\s+system boot\s+(?P<kernel>[^\s]+)?\s+(?P<start>\w{3}\s+\w{3}\s+\d+\s+\d{2}:\d{2})"
        r"(?:\s+-\s+(?P<end>[^()]+))?(?:\s+\((?P<duration>[^)]+)\))?"
    )

    for line in lines:
        if not line.startswith("reboot"):
            continue

        match = RE_BOOT_LINE.match(line)
        if not match:
            continue

        start_str = match.group("start")
        try:
            start_dt = datetime.strptime(f"{year} {start_str}", "%Y %a %b %d %H:%M")
        except ValueError:
            continue

        parsed_entries.append({
            "type": match.group("type"),
            "kernel": match.group("kernel") or "-",
            "start_dt": start_dt,
            "duration": match.group("duration"),
            "end": (match.group("end") or "").strip()
        })

    parsed_entries.sort(key=lambda x: x["start_dt"], reverse=True)
    return parsed_entries

def format_duration(duration_str):
    """Convert raw duration string into human-readable format."""
    if not duration_str or duration_str.strip() == "00:00":
        return "a few sec"

    if "+" in duration_str:
        days_part, time_part = duration_str.split("+")
        days = int(days_part.strip())
        hours, minutes = map(int, time_part.strip().split(":"))
        return f"{days}d {hours}h {minutes}m"
    else:
        hours, minutes = map(int, duration_str.strip().split(":"))
        return f"{hours}h {minutes}m"

def parse_duration(duration_str):
    """Convert a duration string into dict for timedelta."""
    if not duration_str:
        return {"days": 0, "hours": 0, "minutes": 0}
    if "+" in duration_str:
        days_part, time_part = duration_str.split("+")
        days = int(days_part.strip())
        hours, minutes = map(int, time_part.strip().split(":"))
    else:
        days = 0
        hours, minutes = map(int, duration_str.strip().split(":"))
    return {"days": days, "hours": hours, "minutes": minutes}

def format_timedelta(td: timedelta):
    """Convert timedelta to human-readable uptime string."""
    total_seconds = int(td.total_seconds())
    days = total_seconds // (24 * 3600)
    hours = (total_seconds % (24 * 3600)) // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show boot history with optional date format.")
    parser.add_argument("--long-date", action="store_true", help="Display date as 'May 05, 2025' instead of '2025-05-05'")
    args = parser.parse_args()

    entries = parse_last_output()
    use_long_date = args.long_date
    console = Console()
    now = datetime.now()

    table = Table(box=MINIMAL_HEAVY_HEAD, show_lines=False)
    table.add_column("Boot Time", style="bright_cyan", no_wrap=True, justify="left")
    table.add_column("Shutdown", style="bright_blue", no_wrap=True, justify="left")
    table.add_column("Uptime", style="green", justify="center")
    table.add_column("Exit", justify="center")
    table.add_column("Kernel", style="yellow", justify="right")

    for entry in entries:
        for i, entry in enumerate(entries):
    start_dt = entry["start_dt"]
    boot_time = start_dt.strftime("%b %d, %Y %H:%M") if use_long_date else start_dt.strftime("%Y-%m-%d %H:%M")
    end = entry["end"]
    duration = entry["duration"]

    shutdown = "unknown"
    uptime = "?"
    exit_label = "?"

    if end == "still running":
        shutdown = "still running"
        uptime = format_timedelta(now - start_dt)
        exit_label = "running"

    elif end == "crash":
        if duration:
            delta = timedelta(**parse_duration(duration))
            shutdown_dt = start_dt + delta
            shutdown = shutdown_dt.strftime("%b %d, %Y %H:%M") if use_long_date else shutdown_dt.strftime("%Y-%m-%d %H:%M")
            uptime = format_duration(duration)
        exit_label = "crash"

    elif duration:
        delta = timedelta(**parse_duration(duration))
        shutdown_dt = start_dt + delta
        shutdown = shutdown_dt.strftime("%b %d, %Y %H:%M") if use_long_date else shutdown_dt.strftime("%Y-%m-%d %H:%M")
        uptime = format_duration(duration)
        exit_label = "shutdown"

    else:
        # neither 'end' nor 'duration' exists, estimate duration via next entry
        if i + 1 < len(entries):
            next_start = entries[i + 1]["start_dt"]
        else:
            next_start = now

        shutdown_dt = next_start
        delta = shutdown_dt - start_dt
        uptime = format_timedelta(delta)
        shutdown = shutdown_dt.strftime("%b %d, %Y %H:%M") if use_long_date else shutdown_dt.strftime("%Y-%m-%d %H:%M")
        exit_label = "shutdown"

    exit_text = Text(exit_label)
    exit_styles = {
        "crash": "bold red",
        "shutdown": "bright_blue",
        "running": "green"
    }
    exit_text.stylize(exit_styles.get(exit_label, "white"))

    table.add_row(
        boot_time,
        shutdown,
        uptime,
        exit_text,
        entry["kernel"]
    )
