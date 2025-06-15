import subprocess

def shell_escape(s):
    """Shell özel karakterlerini escape et"""
    escaped = ''
    for c in s:
        if c in ['"', '\\', '$', '`']:
            escaped += '\\'
        escaped += c
    return escaped

def get_input_from_rofi(options: list, prompt: str, theme=None, flags=None) -> str:
    """
    Kullanıcıya rofi menüsü gösterir ve seçimi döner.

    :param prompt: Rofi başlığı
    :param options: Gösterilecek seçenek listesi
    :param theme: (Opsiyonel) Rofi tema dosyası (örnek: '/path/to/theme.rasi')
    :param flags: (Opsiyonel) Rofi için ekstra bayraklar listesi (örnek: ['-someflag', 'value'])
    :return: Kullanıcının seçtiği seçenek (str)
    """
    rofi_flags = flags or []

    if theme:
        rofi_flags += ['-theme', theme]

    rofi_cmd = ['rofi', '-dmenu', '-p', prompt] + rofi_flags

    try:
        result = subprocess.run(
            rofi_cmd,
            input='\n'.join(options),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        return result.stdout.strip()
    except Exception as e:
        print("Rofi çalıştırılırken hata:", e)
        return ""
