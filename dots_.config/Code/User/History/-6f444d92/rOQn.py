import os
import time
import sys
import json
import webbrowser
import requests
import http.server
import threading
from urllib.parse import urlparse, parse_qs
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
    token_holder = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/callback":
                # Token iframe'den post edilmiş query parametre olarak geliyor
                query = parse_qs(parsed.query)
                if "access_token" in query:
                    token_holder["token"] = query["access_token"][0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<h1>Yetkilendirme tamamlandi. Terminale donebilirsiniz.</h1>")
                else:
                    # Eğer direk GET olursa token yok, html dön
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    # Token'ı URL fragment (#) olarak alan ve POST ile buraya gönderen sayfa
                    self.wfile.write("""
<html>
<body>
<h1>Yetkilendirme devam ediyor...</h1>
<script>
  // URL fragment'tan access_token al ve query parametre olarak post et
  const hash = window.location.hash.substr(1);
  const params = new URLSearchParams(hash);
  const token = params.get("access_token");
  if(token) {
    // Token'ı URL query parametre olarak yolla
    fetch(window.location.pathname + "?access_token=" + token).then(() => {
      document.body.innerHTML = "<h2>Token alındı, terminale dönebilirsiniz.</h2>";
    });
  } else {
    document.body.innerHTML = "<h2>Token alınamadı.</h2>";
  }
</script>
</body>
</html>
""".encode("utf-8"))

            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            # Logları kapat (isteğe bağlı)
            return

    server = http.server.HTTPServer(("localhost", 8765), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    auth_url = (
        f"https://anilist.co/api/v2/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=token"
    )
    print("🔗 Tarayıcı açılıyor...")
    webbrowser.open(auth_url)

    print("🔑 Kullanıcı giriş yapıyor, bekleniyor...")
    while "token" not in token_holder:
        time.sleep(0.5)

    server.shutdown()
    server.server_close()

    token = token_holder["token"]
    save_token(token)
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
