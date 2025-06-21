import subprocess
import re
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table

def parse_datetime(date_str):
    # Örnek input: "Mon Jun 16 22:34"
    now = datetime.now()
    dt = datetime.strptime(date_str, "%a %b %d %H:%M")
    dt = dt.replace(year=now.year)
    # Eğer dt bugünden sonraysa (gelecekteyse) geçen yıla çek
    if dt > now + timedelta(days=1):
        dt = dt.replace(year=now.year - 1)
    return dt

def parse_last_output():
    # last -x çıktısını al
    result = subprocess.run(["last", "-x"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")

    parsed_entries = []

    for line in lines:
        # Sadece reboot, shutdown, runlevel içeren satırları al
        if not line.startswith(("reboot", "shutdown", "runlevel")):
            continue

        # Regex ile parse et
        match = re.match(
            r"(?P<type>\w+)\s+system (?:boot|down|runlevel)\s+(?P<kernel>[\w\.\-\*]+)?\s+(?P<start>\w{3}\s+\w{3}\s+\d+\s+\d+:\d+)(?:\s+-\s+(?P<end>\w{3}\s+\d+:\d+|\d+:\d+|crash|down|still running))?\s+\((?P<duration>[^)]+)\)", 
            line
        )

        if not match:
            continue  # regex eşleşmeyen satırları atla

        parsed = {
            "type": match.group("type"),  # reboot, shutdown, runlevel
            "kernel": match.group("kernel") or "-",
            "start_str": match.group("start"),
            "start": parse_datetime(match.group("start")),  # datetime objesi
            "end": match.group("end") or "still running",
            "duration": match.group("duration"),
        }

        parsed_entries.append(parsed)

    return parsed_entries


if __name__ == "__main__":
    entries = parse_last_output()
    console = Console()

    table = Table(title="Boot Sessions", show_lines=True)
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Boot Time", style="magenta")
    table.add_column("Shutdown", style="magenta")
    table.add_column("Uptime", style="green")
    table.add_column("Exit", style="red")
    table.add_column("Kernel", style="yellow")

    for i, e in enumerate(entries, 1):
        # Shutdown zamanı: eğer 'end' özel bir durumsa direkt yaz, değilse string kalacak
        shutdown_time = e["end"]
        # Boot time formatı
        boot_time = e["start"].strftime("%Y-%m-%d %H:%M")
        # Çıkış tipi
        exit_type = e["type"]

        table.add_row(str(i), boot_time, shutdown_time, e["duration"], exit_type, e["kernel"])

    console.print(table)
