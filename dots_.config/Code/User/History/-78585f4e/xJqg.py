from packaging import version
import requests
import os
import shutil
import subprocess
from . import config

def get_latest_version():
    url = f"https://api.github.com/repos/{config.GITHUB_REPO}/releases/latest"
    response = requests.get(url)
    tag = response.json()["tag_name"]
    return tag.lstrip("v")  # "vx.x.x" → "x.x.x"

def download_and_replace_binary():
    url = f"https://raw.githubusercontent.com/{config.GITHUB_REPO}/main/update-anitr-cli.sh"
    temp_path = "/tmp/update-anitr-cli.sh"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Hata: update script indirilemedi → {e}")
        return

    with open(temp_path, "wb") as f:
        f.write(response.content)

    subprocess.run(["chmod", "+x", temp_path], check=True)

    print("📦 Güncelleme başlatılıyor...")

    # Python işlemini sonlandır ve update scriptini çalıştır
    os.execv(temp_path, [temp_path])


def check_update_notice():
    try:
        latest = get_latest_version()
        if version.parse(latest) > version.parse(config.CURRENT_VERSION):
            notice = f"Yeni bir anitr-cli sürümü mevcut: {config.CURRENT_VERSION} → {latest}\n" \
                     f"Güncellemek için şunu çalıştırın: anitr-cli --update"
            
            return notice
    except Exception:
        pass
