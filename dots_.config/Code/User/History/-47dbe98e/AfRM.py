import subprocess
import re
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table

def parse_datetime(date_str, year):
    # Tarihleri datetime objesine dönüştür
    return datetime.strptime(f"{year} {date_str}", "%Y %a %b %d %H:%M")

def parse_last_output():
    # last -x çıktısını al
    result = subprocess.run(["last", "-x"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")

    year = datetime.now().year
    reboot_entries = []
    shutdown_entries = []

    # Verileri ayır: reboot ve shutdown
    for line in lines:
        if line.startswith("reboot"):
            match = re.match(
                r"(?P<type>reboot)\s+system boot\s+(?P<kernel>[\w\.\-\*]+)?\s+(?P<start>\w{3}\s+\w{3}\s+\d+\s+\d+:\d+)\s+-\s+(?P<end>\w{3}\s+\d+:\d+|\d+:\d+|crash|down|still running)?\s+\((?P<duration>[^)]+)\)", 
                line
            )
            if match:
                reboot_entries.append({
                    "start_str": match.group("start"),
                    "kernel": match.group("kernel") or "-",
                    "duration": match.group("duration"),
                    "raw_end": match.group("end") or "still running"
                })

        elif line.startswith("shutdown"):
            match = re.match(
                r"shutdown\s+system down\s+(?P<kernel>[\w\.\-\*]+)?\s+(?P<shutdown>\w{3}\s+\w{3}\s+\d+\s+\d+:\d+).*?(?P<end>crash)?", 
                line
            )
            if match:
                shutdown_entries.append({
                    "shutdown_str": match.group("shutdown"),
                    "is_crash": bool(match.group("end"))
                })

    return reboot_entries, shutdown_entries

def find_corresponding_shutdown(reboot_start_dt, shutdowns):
    for entry in shutdowns:
        shutdown_dt = datetime.strptime(f"{datetime.now().year} {entry['shutdown_str']}", "%Y %a %b %d %H:%M")
        if shutdown_dt > reboot_start_dt:
            return shutdown_dt, entry["is_crash"]
    return None, False  # eşleşme yoksa

if __name__ == "__main__":
    reboots, shutdowns = parse_last_output()
    console = Console()

    table = Table(title="Boot Sessions", show_lines=True)
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Boot Time", style="magenta")
    table.add_column("Shutdown", style="magenta")
    table.add_column("Uptime", style="green")
    table.add_column("Exit", style="red")
    table.add_column("Kernel", style="yellow")

    for i, entry in enumerate(reboots, 1):
        # Boot time'ı datetime'a çevir
        start_dt = datetime.strptime(f"{datetime.now().year} {entry['start_str']}", "%Y %a %b %d %H:%M")
        # Shutdown eşleştir
        shutdown_dt, is_crash = find_corresponding_shutdown(start_dt, shutdowns)

        boot_time = start_dt.strftime("%Y-%m-%d %H:%M")
        duration = entry["duration"]

        if shutdown_dt:
            shutdown_str = shutdown_dt.strftime("%Y-%m-%d %H:%M")
        else:
            # crash varsa ya da still running ise shutdown bilinmiyor
            shutdown_str = "still running"

        exit_reason = "crash" if is_crash else ("shutdown" if shutdown_dt else "running")

        table.add_row(
            str(i),
            boot_time,
            shutdown_str,
            duration,
            exit_reason,
            entry["kernel"]
        )

    console.print(table)
