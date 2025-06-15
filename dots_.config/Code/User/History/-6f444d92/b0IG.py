import os
import time
import sys
import json
import webbrowser
import requests

from InquirerPy import inquirer, prompt
from InquirerPy.validator import ValidationError

CLIENT_ID = "27657" 
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
TOKEN_FILE = "token.json"

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def show_error(msg: str, sleep: float = 2):
    print(f"\033[91m[!] - {msg}\033[0m")
    time.sleep(sleep)

def not_empty_validator(val):
    if len(val.strip()) == 0:
        raise ValidationError(message="Boş bırakılamaz.")
    return True

def get_selection_from_list(choices: list, message: str = "Bir seçenek seçin:", Type: str = "fuzzy", header=None) -> str:
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
    return result["selection"]

def get_token():
    if not os.path.exists(TOKEN_FILE):
        show_error("Lütfen önce `python script.py auth` ile yetkilendirme yapın.")
        sys.exit(1)
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)["access_token"]

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": token}, f)
    print("✅ Token kaydedildi.")

def do_auth():
    print("🔑 Anilist hesabınızla giriş yapmanız gerekiyor.")

    # Adım 1: Yetkilendirme linki
    auth_url = f"https://anilist.co/api/v2/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    print(f"\n🔗 Bu bağlantıya tarayıcıdan gidin ve giriş yapın:\n\n{auth_url}\n")
    webbrowser.open(auth_url)

    # Adım 2: Kullanıcıdan code al
    code = input("🔑 Tarayıcıda dönen URL'deki `code=` parametresini buraya yapıştırın:\n> ").strip()

    # Adım 3: Token alma
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": "",  # Eğer bir client secret varsa (seninki public client ise olmayabilir)
        "redirect_uri": REDIRECT_URI,
        "code": code
    }

    response = requests.post("https://anilist.co/api/v2/oauth/token", data=data)
    if response.status_code != 200:
        show_error(f"Token alınamadı! Kod: {response.status_code}\n\n{response.text}")
        return

    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        show_error("Erişim anahtarı alınamadı!")
        return

    save_token(access_token)
    print("✅ Başarıyla giriş yapıldı!")


def fetch_list(media_type="ANIME"):
    token = get_token()
    query = '''
    query ($type: MediaType) {
      Viewer {
        id
        name
        mediaListOptions {
          scoreFormat
        }
        mediaListCollection(type: $type) {
          lists {
            name
            entries {
              media {
                title {
                  romaji
                  english
                }
              }
            }
          }
        }
      }
    }
    '''
    variables = {"type": media_type}
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://graphql.anilist.co"

    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code != 200:
        show_error("API hatası. Token geçersiz olabilir.")
        return []

    data = response.json()
    media_list = []
    for section in data["data"]["Viewer"]["mediaListCollection"]["lists"]:
        for entry in section["entries"]:
            title = entry["media"]["title"]["english"] or entry["media"]["title"]["romaji"]
            media_list.append(title)
    return media_list

def main():
    anime_list = fetch_list("ANIME")
    manga_list = fetch_list("MANGA")

    choice = get_selection_from_list(
        ["📺 Anime Listesi", "📖 Manga Listesi"], message="Hangi listeyi görmek istersin?"
    )

    selected_list = anime_list if "Anime" in choice else manga_list
    if not selected_list:
        show_error("Liste boş.")
        return

    choice = get_selection_from_list(selected_list, message="Bir eser seç:")
    print(f"\n✅ Seçilen: {choice}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        do_auth()
    else:
        main()
