from InquirerPy import inquirer, prompt
from InquirerPy.validator import ValidationError
import os, time

def clear_screen():
    """Ekranı temizle"""
    os.system("clear")

def show_error(msg: str, sleep: float):
    print(f"\033[91m[!] - {msg}\033[0m")
    time.sleep(sleep)

def not_empty_validator(val):
    if len(val.strip()) == 0:
        raise ValidationError(message="Boş bırakılamaz.")
    return True

def validation_error(msg: str):
    raise ValidationError(message=msg)

def get_selection_from_list(choices: list, message: str = "Bir seçenek seçin:", Type: str = "fuzzy", header=None) -> str:
    """
    Kullanıcıya seçeneklerden birini seçtiren menü.

    Parametreler:
        choices (list): Seçenek listesi (örnek: ["animecix", "openanime"])
        message (str): Ekranda gösterilecek açıklama (varsayılan: "Bir seçenek seçin:")

    Döndürür:
        str: Kullanıcının seçtiği öğe

    Notlar:
        - Seçenekler arasında yazı yazarak arama yapılabilir (fuzzy search).
        - Yukarı/aşağı ok tuşları ile gezilebilir.
        - Enter ile seçim yapılır, ESC ile çıkılabilir.
    """
    clear_screen()
    if header:
        print(header)
        
    question = [
        {
            "type": Type,
            "name": "selection",
            "message": message,
            "choices": choices,
            "border": True,
            "cycle": True,
            "max_height": "70%",
        }
    ]
    result = prompt(question)
    return result["selection"] # type: ignore


def get_input_from_user(message: str = "Bir şey yazın:") -> str:
    """
    Kullanıcıdan serbest metin girişi alır.

    Parametreler:
        message (str): Kullanıcıya gösterilecek mesaj

    Döndürür:
        str: Kullanıcının yazdığı metin

    Notlar:
        - Giriş boş olamaz. Boş geçmeye çalışırsa hata mesajı gösterilir.
        - Yazılan değer direkt string olarak döndürülür.
    """
    clear_screen()
    result = inquirer.text(
        message=message,
        validate=not_empty_validator
    ).execute()
    return result