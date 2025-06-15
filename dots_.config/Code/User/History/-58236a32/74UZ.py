import os
import time
import json
from pypresence import Client

class DiscordRPC:
    def __init__(self, client_id):
        self.client_id = client_id
        self.rpc = Client(client_id)
        self.connected = False

    def connect(self):
        """Discord RPC bağlantısını başlat."""
        if not self.connected:
            self.rpc.start()
            self.connected = True

    def create(self, filepath):
        """Dosyadan veriyi okuyup RPC etkinliği oluştur."""
        try:
            self.connect()
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._set_activity(data)
            print("📺 RPC etkinliği başarıyla ayarlandı.")
        except Exception as e:
            print(f"Error: {e}")

    def update(self, filepath):
        """Etkinlik verisini güncelle."""
        if not self.connected:
            raise RuntimeError("RPC bağlantısı yok. Önce create() çağırılmalı.")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._set_activity(data)
        except Exception as e:
            print(f"Error: {e}")

    def stop(self):
        """RPC etkinliğini temizle ve bağlantıyı sonlandır."""
        if self.connected:
            self.rpc.clear_activity()
            self.rpc.close()
            self.connected = False
            print("RPC bağlantısı kapatıldı.")

    def _set_activity(self, data):
        """Etkinlik verisini Discord'a gönder."""
        activity = {
            "pid": os.getpid(),
            "activity": {
                "type": 3,  # 🎬 Watching
                "details": data.get("details"),
                "state": data.get("state"),
                "timestamps": {
                    "start": int(time.time())  # Başlangıç zamanını ekliyoruz
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

        # send_data ile aktiviteyi Discord'a gönderiyoruz
        self.rpc.send_data(1, {
            "cmd": "SET_ACTIVITY",
            "args": activity,
            "nonce": str(time.time())
        })

