import os
import time
import json
from pypresence import Client

class DiscordRPC:
    def __init__(self):
        client_id = "1383421771159572600"
        self.client_id = client_id
        self.rpc = Client(client_id)
        self.start_time = int(time.time())
        self.connected = False

    def connect(self):
        if not self.connected:
            self.rpc.start()
            self.connected = True

    def create(self, filepath):
        try:
            self.connect()
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._set_activity(data, include_timestamp=data.get("timestamps", False))
            print("RPC activity set successfully.")

            # RPC'yi sürekli aktif tutmak için bir loop ekleyelim
            while True:
                self.update(filepath)
                time.sleep(15)  # Her 15 saniyede bir güncelleme yapacak

        except Exception as e:
            print(f"Discord RPC create() error: {e}")

    def update(self, filepath):
        if not self.connected:
            raise RuntimeError("RPC bağlantısı yok. Önce create() çağırılmalı.")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._set_activity(data, include_timestamp=False)
        except Exception as e:
            print(f"Discord RPC update() error: {e}")

    def stop(self):
        if self.connected:
            self.rpc.clear_activity()
            self.rpc.close()
            self.connected = False

    def _set_activity(self, data, include_timestamp=True):
        activity = {
            "pid": os.getpid(),
            "activity": {
                "type": 3,
                "details": data.get("details"),
                "state": data.get("state"),
                "assets": {
                    "large_image": data.get("large_image"),
                    "large_text": data.get("large_text"),
                    "small_image": data.get("small_image"),
                    "small_text": data.get("small_text")
                },
                "buttons": data.get("buttons", [])
            }
        }

        if include_timestamp:
            activity["activity"]["timestamps"] = {
                "start": self.start_time
            }

        # Send the data to Discord
        self.rpc.send_data(1, {
            "cmd": "SET_ACTIVITY",
            "args": activity,
            "nonce": str(time.time())
        })
