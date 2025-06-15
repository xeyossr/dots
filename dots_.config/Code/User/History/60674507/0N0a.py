import rofi_menu as rofi
import tui_menu as tui
from dotenv import load_dotenv
import os

load_dotenv(os.path.expanduser("~/.config/anitr-cli/config"))

def parse_config_file():
    """~/.config/anitr-cli/config içinden gerekli ayarları alan funksiyon"""
    flags_str = os.getenv("ROFI_FLAGS", "")
    theme_from_config = os.getenv("ROFI_THEME")
    default_ui = os.getenv("DEFAULT_UI")
    flags = flags_str.split()
    return flags, theme_from_config

rofi_theme, rofi_flags = parse_config_file()

def search_menu(type: str = "tui", msg: str = "Anime Ara"):
    if type.lower() == "tui":
        return tui.get_input_from_user(msg)
    elif type.lower() == "rofi":
        return rofi.get_input_from_rofi(["Çık"], msg, rofi_theme, rofi_flags)

def select_menu(type: str = "tui", choices: list, msg: str):
    if type.lower() == "tui":
        return tui.get_selection_from_list(choices, msg)
    elif type.lower() == "rofi":
        return rofi.get_input_from_rofi(choices, msg, rofi_theme, rofi_flags)