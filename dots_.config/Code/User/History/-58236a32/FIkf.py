from pypresence import Client
import time
import os

client_id = "1383421771159572600"
rpc = Client(client_id)
rpc.start()

start_time = int(time.time())

def get_activity():
    return {
        "pid": os.getpid(),
        "activity": {
            "type": 3,  # Watching
            "details": "Watching Vinland Saga",
            "state": f"Season 2, Episode 4",
            "timestamps": {
                "start": start_time
            },
            "assets": {
                "large_image": "anitrcli",
                "small_image": "openanime",
                "small_text": "OpensAnime"
            },
            "buttons": [
                {"label": "OpenAnime", "url": "https://openani.me"},
                {"label": "Repo", "url": "https://github.com/xeyossr/anitr-cli"}
            ]
        }
    }

try:
    while True:
        rpc.send_data(1, {
            "cmd": "SET_ACTIVITY",
            "args": get_activity(),
            "nonce": str(time.time())
        })
        time.sleep(15)  # Discord'un önerdiği güncelleme süresi
except KeyboardInterrupt:
    print("\nEtkinlik temizleniyor...")
    rpc.clear_activity()
    print("Çıkış yapıldı.")
