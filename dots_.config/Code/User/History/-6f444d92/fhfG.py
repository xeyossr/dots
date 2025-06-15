import os
import time
import sys
import json
import webbrowser
import requests
import http.server
import threading
from InquirerPy import inquirer, prompt
from InquirerPy.validator import ValidationError

CLIENT_ID = "27657" 
REDIRECT_URI = "http://localhost:8765/callback"
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
    return result["selection"] # type: ignore

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
    code_holder = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            if "code" in query:
                code_holder["code"] = query["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Yetkilendirme tamamlandi. Terminale donebilirsiniz.</h1>")
            else:
                self.send_response(400)
                self.end_headers()

    # Localhost dinleyicisi
    server = http.server.HTTPServer(("localhost", 8765), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Tarayıcıyı aç
    import webbrowser
    auth_url = f"https://anilist.co/api/v2/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    print("🔗 Tarayıcı açılıyor...")
    webbrowser.open(auth_url)

    # Kod gelene kadar bekle
    print("🔑 Kullanıcı giriş yapıyor, bekleniyor...")
    while "code" not in code_holder:
        time.sleep(0.5)

    # Server kapat
    server.shutdown()
    server.server_close()

    # Şimdi token'ı al
    code = code_holder["code"]
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": "",  # Gerekirse ekle
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    response = requests.post("https://anilist.co/api/v2/oauth/token", data=data)
    if response.status_code != 200:
        show_error(f"Token alınamadı:\n{response.text}")
        return

    access_token = response.json().get("access_token")
    save_token(access_token)
    print("✅ Token başarıyla alındı!")


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
