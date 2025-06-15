from modules.rpc import DiscordRPC
import time

# Discord uygulama ID'si
client_id = "1383421771159572600"
rpc = DiscordRPC(client_id)

# Dosyadan etkinlik bilgilerini oluşturuyoruz
rpc.create("/tmp/anime_details")

# Etkinliği 15 saniye gösteriyoruz
time.sleep(15)

# RPC'yi kapatıyoruz
rpc.stop()
