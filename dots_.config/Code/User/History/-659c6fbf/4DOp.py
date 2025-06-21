import os
import json

from pypresence import Client
from . import config
from . import utils

def log_anime_details(details: str, state: str, large_text: str, source: str, source_url: str, path=config.anime_details):
    data = {
        "details": f"Watching {details}",
        "state": state,
        "large_image": "anitrcli",
        "large_text": large_text,
        "small_image": source.lower(),
        "small_text": source,
        "buttons": [
            {"label": source, "url": source_url},
            {"label": "GitHub", "url": config.github_repo}
        ]
    }
    with open(path, "w", encoding="utf-8") as tmpf:
        json.dump(data, tmpf, indent=2, ensure_ascii=False)

def start_discord_rpc(client_id=config.discord_client_id, filepath=config.anime_details):
    if config.rpc_initialized:
        update_discord_rpc(filepath)
        return
    
    try:
        if config.rpc is None:
            config.rpc = Client(client_id)
            config.rpc.start()
            config.rpc_initialized = True
    except Exception as e:
        config.rpc = None
        config.rpc_initialized = False
        utils.log_error(config.error_log, e)
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        utils.log_error(config.error_log, e)
        return

    activity = {
        "pid": os.getpid(),
        "activity": {
            "type": 3,
            "details": data.get("details"),
            "state": data.get("state"),
            "timestamps": {
                "start": config.start_time
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
        config.rpc.send_data(1, {
            "cmd": "SET_ACTIVITY",
            "args": activity,
            "nonce": "watching-anime"
        })
    except Exception as e:
        utils.log_error(config.error_log, e)

def update_discord_rpc(filepath=config.anime_details):
    if not config.rpc_initialized:
        start_discord_rpc()
        if not config.rpc_initialized:
            return

    if config.rpc is None:
        start_discord_rpc()
        if config.rpc is None:
            return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        utils.log_error(config.error_log, e)

    activity = {
        "pid": os.getpid(),
        "activity": {
            "type": 3,
            "details": data.get("details"),
            "state": data.get("state"),
            "timestamps": {
                "start": config.start_time
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
        config.rpc.send_data(1, {
            "cmd": "SET_ACTIVITY",
            "args": activity,
            "nonce": "watching-anime"
        })
    except Exception as e:
        utils.log_error(config.error_log, e)

def stop_discord_rpc():
    if config.rpc:
        config.rpc.clear_activity()
        config.rpc.close()
        config.rpc = None
