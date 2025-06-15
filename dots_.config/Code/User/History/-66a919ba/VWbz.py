import os
import time
from pypresence import Client

class DiscordRPC:
    def __init__(self, client_id):
        self.client_id = client_id
        self.rpc = Client(client_id)

    def connect(self):
        self.rpc.start()

    def set_activity(self, activity_data):
        self.rpc.send_data(1, {
            "cmd": "SET_ACTIVITY",
            "args": activity_data,
            "nonce": str(time.time())
        })

    def clear_activity(self):
        self.rpc.clear_activity()

    def stop(self):
        self.clear_activity()
        self.rpc.close()

# Etkinlik bilgilerini içeren json verisi
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

# Modül kullanımı
rpc = DiscordRPC(client_id="1383421771159572600")
rpc.connect()
rpc.set_activity(activity)

print("📺 Watching etkinliği gönderildi.")
input("Çıkmak için enter'a bas...")

rpc.stop()
