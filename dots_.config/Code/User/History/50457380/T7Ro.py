import subprocess
import os

def shell_escape(s):
    """Shell özel karakterlerini escape et"""
    escaped = ''
    for c in s:
        if c in ['"', '\\', '$', '`']:
            escaped += '\\'
        escaped += c
    return escaped

def parse_config_file():
    """~/.config/anitr-cli/config içinden ROFI_FLAGS ve ROFI_THEME ayarlarını alır"""
    flags = []
    theme_from_config = None
    config_path = os.path.expanduser("~/.config/anitr-cli/config")

    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("ROFI_FLAGS="):
                    flags_str = line[len("ROFI_FLAGS="):].strip()
                    flags.extend(flags_str.split())
                elif line.startswith("ROFI_THEME="):
                    theme_from_config = line[len("ROFI_THEME="):].strip()

    return flags, theme_from_config

def get_input_from_rofi(prompt, options, theme=None):
    """
    Kullanıcıya rofi menüsü gösterir ve seçimi döner.

    :param prompt: Rofi başlığı
    :param options: Gösterilecek seçenek listesi
    :param theme: (Opsiyonel) Rofi tema dosyası (örnek: '/path/to/theme.rasi')
    :return: Kullanıcının seçtiği seçenek (str)
    """
    config_flags, config_theme = parse_config_file()
    rofi_flags = config_flags

    # Theme: parametre verilmişse onu kullan, yoksa config'tekini
    selected_theme = theme or config_theme
    if selected_theme:
        rofi_flags += ['-theme', selected_theme]

    # Rofi komutu
    rofi_cmd = ['rofi', '-dmenu', '-p', prompt] + rofi_flags

    try:
        result = subprocess.run(
            rofi_cmd,
            input='\n'.join(options),
            text=True,
            capture_output=True,
            stderr=subprocess.DEVNULL
        )
        return result.stdout.strip()
    except Exception as e:
        print("Rofi çalıştırılırken hata:", e)
        return ""
