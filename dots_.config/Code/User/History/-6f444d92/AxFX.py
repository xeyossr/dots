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

CLIENT_ID = None
CLIENT_SECRET = None
REDIRECT_URI = "http://localhost:8765/callback"
TOKEN_FILE = "token.json"
CONFIG_FILE = "config.json"

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
    return result["selection"]  # type: ignore

def get_input_from_user(message: str = "Bir şey yazın:") -> str:
    clear_screen()
    print("⚠️  Redirect URI kısmına http://localhost:8765/callback girilmeli!")
    result = inquirer.text(
        message=message,
        validate=not_empty_validator
    ).execute()
    return result

def save_config(client_id, client_secret):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"client_id": client_id, "client_secret": client_secret}, f)

def load_config():
    global CLIENT_ID, CLIENT_SECRET
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            CLIENT_ID = data.get("client_id")
            CLIENT_SECRET = data.get("client_secret")

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": token}, f)
    print("✅ Token kaydedildi.")

def get_token():
    if not os.path.exists(TOKEN_FILE):
        show_error("Lütfen önce `python script.py auth` ile yetkilendirme yapın.")
        sys.exit(1)
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)["access_token"]

def do_auth():
    global CLIENT_ID, CLIENT_SECRET

    load_config()
    if not CLIENT_ID:
        CLIENT_ID = get_input_from_user("Client ID girin:")
    if not CLIENT_SECRET:
        CLIENT_SECRET = get_input_from_user("Client Secret girin:")
    save_config(CLIENT_ID, CLIENT_SECRET)

    token_holder = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            # token implicit grant ile gelmez queryde, hash fragmentte gelir ama bunu tarayıcıdan yakalayamazsın,
            # burada authorization code ile devam edeceğiz
            if "code" in query:
                token_holder["code"] = query["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Yetkilendirme tamamlandi. Terminale donebilirsiniz.</h1>")
            else:
                self.send_response(400)
                self.end_headers()

        def log_message(self, format, *args):
            return  # logları kapat

    server = http.server.HTTPServer(("localhost", 8765), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    auth_url = (
        f"https://anilist.co/api/v2/oauth/authorize?"
        f"client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    )
    print("🔗 Tarayıcı açılıyor...")
    webbrowser.open(auth_url)

    print("🔑 Kullanıcı giriş yapıyor, bekleniyor...")
    while "code" not in token_holder:
        time.sleep(0.5)

    server.shutdown()
    server.server_close()

    code = token_holder["code"]
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }

    response = requests.post("https://anilist.co/api/v2/oauth/token", data=data)
    if response.status_code != 200:
        show_error(f"Token alınamadı:\n{response.text}")
        sys.exit(1)

    access_token = response.json().get("access_token")
    if not access_token:
        show_error("Token alınamadı. Yanıt incelenmeli.")
        sys.exit(1)
    save_token(access_token)
    print("✅ Token başarıyla alındı!")

def fetch_user_id(token):
    url = "https://graphql.anilist.co"
    query = '''
    query {
      Viewer {
        id
        name
      }
    }
    '''
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json={"query": query}, headers=headers)
    if response.status_code != 200:
        show_error("Kullanıcı bilgisi alınamadı. Token geçersiz olabilir.")
        return None
    data = response.json()
    return data.get("data", {}).get("Viewer", {}).get("id", None)

def fetch_list(token, media_type="ANIME"):
    url = "https://graphql.anilist.co"
    query = '''
    query ($type: MediaType) {
      Viewer {
        mediaList(type: $type) {
          id
          status
          score
          media {
            id
            title {
              romaji
              english
            }
          }
        }
      }
    }
    '''
    variables = {"type": media_type}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code != 200:
        show_error("API hatası. Token geçersiz olabilir.")
        return []

    data = response.json()
    if "errors" in data:
        show_error(f"API hatası: {data['errors']}")
        return []

    media_list = []
    viewer = data.get("data", {}).get("Viewer")
    if not viewer or not viewer.get("mediaList"):
        show_error("Medya listesi bulunamadı veya boş.")
        return []

    for entry in viewer["mediaList"]:
        title = entry["media"]["english"] or entry["media"]["romaji"] or "Bilinmeyen"
        media_list.append(title)
    return media_list


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        do_auth()
        return

    token = get_token()
    user_id = fetch_user_id(token)
    if not user_id:
        show_error("Kullanıcı ID'si alınamadı.")
        return

    anime_list = fetch_list(token, "ANIME")
    manga_list = fetch_list(token, "MANGA")

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
    main()
