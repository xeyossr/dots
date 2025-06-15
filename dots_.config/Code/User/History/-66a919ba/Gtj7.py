from modules.rpc import DiscordRPC as rpc
import time

rpc_instance = rpc()

rpc_instance.create("/tmp/anime_details")