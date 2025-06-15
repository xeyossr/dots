from InquirerPy import inquirer
from InquirerPy.validator import ValidationError
import os

def clear_screen():
    """Ekranı temizle"""
    os.system("clear")


def get_selection_from_list(choices: list, message: str = "Bir seçenek seçin:") -> str:
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
    question = [
        {
            "type": "fuzzy",
            "name": "selection",
            "message": message,
            "choices": choices,
            "border": True,
            "cycle": True,
            "max_height": "70%",
        }
    ]
    result = prompt(question)
    return result["selection"]

def validate_not_empty(val):
    if not val or len(val.strip()) == 0:
        return "Boş bırakılamaz."
    return True

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
        validate=validate_not_empty
    ).execute()
    return result

print(get_input_from_user())