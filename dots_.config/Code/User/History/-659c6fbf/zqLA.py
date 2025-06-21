import os
import json
import config
import utils

from pypresence import Client

def log_anime_details(details: str, state: str, large_text: str, source: str, source_url: str, path: str = "/tmp/anime_details"):
    data = {
        "details": f"Watching {details}",
        "state": state,
        "large_image": "anitrcli",
        "large_text": large_text,
        "small_image": source.lower(),
        "small_text": source,
        "buttons": [
            { "label": source, "url": source_url },
            { "label": "GitHub", "url": "https://github.com/xeyossr/anitr-cli" }
        ]
    }
    
    with open(path, "w", encoding="utf-8") as tmpf:
        json.dump(data, tmpf, indent=2, ensure_ascii=False)

def start_discord_rpc(client_id="1383421771159572600", filepath="/tmp/anime_details"):
    global rpc, rpc_initialized

    if rpc_initialized:
        return
    
    try:
        if rpc is None:
            rpc = Client(client_id)
            rpc.start()
            rpc_initialized = True
    except Exception as e:
        rpc = None
        rpc_initialized = False
        utils.log_error("/tmp/anitr-cli-error.log", e)
        utils.send_notification("anitr-cli", f"Discord RPC başlatılamadı. Hata detayları: /tmp/anitr-cli-error.log", "critical")
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_error("/tmp/anitr-cli-error.log", e)
        send_notification("anitr-cli", f"Discord RPC başlatılamadı. Hata detayları: /tmp/anitr-cli-error.log", "critical")
        return

    activity = {
        "pid": os.getpid(),
        "activity": {
            "type": 3,
            "details": data.get("details"),
            "state": data.get("state"),
            "timestamps": {
                "start": start_time
            },
            "assets": {
                "large_image": data.get("large_image"),
                "large_text": data.get("large_text"),
                "small_image": data.get("small_image"),
                "small_text": data.get("small_text")
            },
            "buttons": data.get("buttons", [])
        }
    }

    try:
        rpc.send_data(1, {
            "cmd": "SET_ACTIVITY",
            "args": activity,
            "nonce": "watching-anime"
        })
    except Exception as e:
        log_error("/tmp/anitr-cli-error.log", e)
        send_notification("anitr-cli", f"Discord RPC başlatılamadı. Hata detayları: /tmp/anitr-cli-error.log", "critical")


def update_discord_rpc(filepath="/tmp/anime_details"):
    global rpc, rpc_initialized

    if not rpc_initialized:
        start_discord_rpc()
        if not rpc_initialized:
            return
    
    if rpc is None:
        start_discord_rpc()
        if rpc is None:
            return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        utils.log_error("/tmp/anitr-cli-error.log", e)
        utils.send_notification("anitr-cli", f"Discord RPC başlatılamadı. Hata detayları: /tmp/anitr-cli-error.log", "critical")

    activity = {
        "pid": os.getpid(),
        "activity": {
            "type": 3,
            "details": data.get("details"),
            "state": data.get("state"),
            "timestamps": {
                "start": start_time
            },
            "assets": {
                "large_image": data.get("large_image"),
                "large_text": data.get("large_text"),
                "small_image": data.get("small_image"),
                "small_text": data.get("small_text")
            },
            "buttons": data.get("buttons", [])
        }
    }

    try:
        rpc.send_data(1, {
            "cmd": "SET_ACTIVITY",
            "args": activity,
            "nonce": "watching-anime"
        })
    except Exception as e:
        utils.log_error("/tmp/anitr-cli-error.log", e)
        utils.send_notification("anitr-cli", f"Discord RPC başlatılamadı. Hata detayları: /tmp/anitr-cli-error.log", "critical")

def stop_discord_rpc():
    global rpc
    if rpc:
        rpc.clear_activity()
        rpc.close()
        rpc = None