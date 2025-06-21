import subprocess
import re
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table

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

    for i, entry in enumerate(entries, 1):
        boot_time = entry["start_dt"].strftime("%Y-%m-%d %H:%M")

        if entry["end"] in ["crash", "down"]:
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
            with open("log.log", "w", encode="utf-8") as log:
                log.write(f"days={days}, hours={hours}, minutes={minutes}")
            shutdown = shutdown_dt.strftime("%Y-%m-%d %H:%M")
            exit_type = "crash"

        elif entry["end"] == "still running":
            shutdown = "still running"
            exit_type = "running"
        else:
            # Saat gibi görünüyorsa sadece zaman vermiştir (örn. 03:12)
            try:
                shutdown_dt = datetime.strptime(entry["end"], "%H:%M")
                shutdown = f"{boot_time[:10]} {entry['end']}"  # sadece saat → tarihi koru
            except ValueError:
                shutdown = entry["end"]
            exit_type = "shutdown"

        table.add_row(
            str(i),
            boot_time,
            shutdown,
            entry["duration"],
            exit_type,
            entry["kernel"]
        )

    console.print(table)
