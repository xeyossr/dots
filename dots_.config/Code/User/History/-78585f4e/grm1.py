from packaging import version
import requests
import os
import shutil
import subprocess

GITHUB_REPO = "xeyossr/anitr-cli"
CURRENT_VERSION = "3.2.0"

def get_latest_version():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    response = requests.get(url)
    tag = response.json()["tag_name"]
    return tag.lstrip("v")  # "vx.x.x" → "x.x.x"

def download_and_replace_binary():
    url = f"https://github.com/{GITHUB_REPO}/releases/latest/download/anitr-cli"
    response = requests.get(url)
    temp_path = "/tmp/anitr-cli"
    
    with open(temp_path, "wb") as f:
        f.write(response.content)

    subprocess.run(["chmod", "+x", temp_path], check=True)

    if os.geteuid() != 0:
        print("🔒 Güncelleme için sudo şifresi gerekli.")
        subprocess.run(["sudo", "cp", temp_path, "/usr/bin/anitr-cli"], check=True)
    else:
        shutil.copy(temp_path, "/usr/bin/anitr-cli")

    print("✅ anitr-cli başarıyla güncellendi.")
