import rofi_menu as rofi
import tui_menu as tui

def search_menu(type: str, msg: str = "Anime Ara"):
    if type.lower() == "tui":
        return tui.get_input_from_user(msg)
    elif type.lower() == "rofi":
        return rofi.get_input_from_rofi(["Çık"], msg)

#search = search_menu("tui", "anime ara")
#print(search)