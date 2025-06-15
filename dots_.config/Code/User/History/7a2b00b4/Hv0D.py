import subprocess
import os
from ytmusicapi import YTMusic

ytmusic = YTMusic()

def mpv_play(url):
    # mpvc komutunu kullanarak şarkıyı çal
    subprocess.run([
        "mpvc", url, "--no-video", "--osc", "--quiet", "--input-ipc-server=/tmp/mpvsocket"
    ])

def ara_ve_çal(aranan):
    # Şarkı araması yap
    sonuçlar = ytmusic.search(aranan, filter="songs")

    if not sonuçlar:
        print("Hiç sonuç bulunamadı.")
        return

    # Kullanıcıya şarkı listesini sun
    for i, şarkı in enumerate(sonuçlar[:10]):
        ad = şarkı.get("title")
        sanatçı = şarkı.get("artists", [{}])[0].get("name", "Bilinmeyen")
        süre = şarkı.get("duration", "?")
        print(f"{i+1}. {ad} - {sanatçı} [{süre}]")

    try:
        # Kullanıcıdan şarkı seçmesini iste
        seçim = int(input("Çalmak istediğiniz şarkının numarası: ")) - 1
        seçilen = sonuçlar[seçim]
    except (ValueError, IndexError):
        print("Geçersiz seçim.")
        return

    video_id = seçilen.get("videoId")
    if video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Şarkı çalınıyor...")

        # mpvc ile şarkıyı çal
        mpv_play(url)
    else:
        print("Video ID bulunamadı.")

if __name__ == "__main__":
    os.system("clear")  # Terminali temizle
    aranan = input("Şarkı adı veya sanatçı: ")  # Kullanıcıdan şarkı adı veya sanatçı adı al
    ara_ve_çal(aranan)  # Şarkıyı ara ve çal
