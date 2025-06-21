import os
import time
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.config/anitr-cli/config"))

default_ui = os.getenv("DEFAULT_UI", "tui")  # Default UI
discord_rpc = os.getenv("DISCORD_RPC", "Enabled")  # RPC açık mı kapalı mı?
sources = ["AnimeciX (anm.cx)", "OpenAnime (openani.me)"]  # Kaynaklar

# Global Discord RPC durumu ve zaman
discord_client_id = "1383421771159572600"
rpc = None
rpc_initialized = False
start_time = int(time.time())

# Paths

