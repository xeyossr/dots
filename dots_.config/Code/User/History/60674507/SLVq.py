from dotenv import load_dotenv
import modules.rofi_ui as rofi
import modules.tui_ui as tui
import os

load_dotenv(os.path.expanduser("~/.config/anitr-cli/config"))

def parse_config_file():
    """~/.config/anitr-cli/config içinden gerekli ayarları alan funksiyon"""
    flags_str = os.getenv("ROFI_FLAGS", "")
    theme_from_config = os.getenv("ROFI_THEME")
    flags = flags_str.split()
    return flags, theme_from_config

rofi_flags, rofi_theme = parse_config_file()

def search_menu(type: str, msg: str = "Anime Ara") -> str:
    if type.lower() == "tui":
        return tui.get_input_from_user(msg)
    elif type.lower() == "rofi":
        return rofi.get_input_from_rofi(["Çık"], msg, rofi_theme, rofi_flags)
    else:
        raise ValueError(f"Unsupported type: {type}")

def select_menu(type: str, choices: list[str], msg: str, tui_menu_with_search_input: bool = True, header=None) -> str:
    if type.lower() == "tui":
        if tui_menu_with_search_input == True:
            return tui.get_selection_from_list(choices, msg, "fuzzy", header)
        elif tui_menu_with_search_input == False:
            return tui.get_selection_from_list(choices, msg, "list", header)
    elif type.lower() == "rofi":
        return rofi.get_input_from_rofi(choices, msg, rofi_theme, rofi_flags)
    else:
        raise ValueError(f"Unsupported type: {type}")

def show_error(type: str, msg: str):
    if type.lower() == "tui":
        tui.show_error(msg, 0.8)
    elif type.lower() == "rofi":
        print(f"\033[91m[!] - {msg}\033[0m")  # kırmızı renkte
    else:
        raise ValueError(f"Unsupported type: {type}")
