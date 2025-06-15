import rofi_menu as rofi
import tui_menu as tui

def search_menu(type: str, msg: str = "Anime Ara"):
    if type.lower() == "tui":
        tui.get_input_from_user(msg)
    elif type.lower() == "rofi":
        rofi.get_input_from_rofi(["Çık"], msg)