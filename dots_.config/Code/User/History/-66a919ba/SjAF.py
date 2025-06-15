from pypresence import Client
import time
import os, json

client_id = "1383421771159572600"  # senin Discord app ID'in
rpc = Client(client_id)
rpc.start()  # Discord IPC bağlantısı kurar

with open("/tmp/anime_details", "r", encoding="utf-8") as f:
    data = json.load(f)

activity = {
    "pid": os.getpid(),
    "activity": {
        "type": 3,  # 🎬 Watching
        "details": "Watching Vinland Saga",
        "state": "Season 2, Episode 4",
        "timestamps": {
            "start": int(time.time())
        },
        "assets": {
            "large_image": "anitrcli",   # Discord geliştirici panelindeki görsel key
            "small_image": "openanime",
            "small_text": "OpenAnime"
        },
        "buttons": [
            {"label": "OpenAnime", "url": "https://openani.me"},
            {"label": "Repo", "url": "https://github.com/xeyossr/anitr-cli"}
        ]
    }
}

rpc.send_data(1, {
    "cmd": "SET_ACTIVITY",
    "args": activity,
    "nonce": "watching-anime"
})

print("📺 Watching etkinliği gönderildi.")
input("Çıkmak için enter'a bas...")
rpc.clear_activity()