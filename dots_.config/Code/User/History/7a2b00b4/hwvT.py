import subprocess
import time, os
from ytmusicapi import YTMusic

ytmusic = YTMusic()

def clear():
    os.system("clear")

def ara_ve_çal(aranan):
    sonuçlar = ytmusic.search(aranan, filter="songs")

    if not sonuçlar:
        print("Hiç sonuç bulunamadı.")
        return

    for i, şarkı in enumerate(sonuçlar[:10]):
        ad = şarkı.get("title")
        sanatçı = şarkı.get("artists", [{}])[0].get("name", "Bilinmeyen")
        süre = şarkı.get("duration", "?")
        print(f"{i+1}. {ad} - {sanatçı} [{süre}]")

    try:
        seçim = int(input("Çalmak istediğiniz şarkının numarası: ")) - 1
        seçilen = sonuçlar[seçim]
    except (ValueError, IndexError):
        print("Geçersiz seçim.")
        return

    video_id = seçilen.get("videoId")
    if video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Şarkı çalınıyor...")

        # YouTube video URL'sinden mp3 indir
        subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # MP3 dosyasını çal
        subprocess.run(["mpg123", "--console", "--visualizer", "spectrum", "song.mp3"])

    else:
        print("Video ID bulunamadı.")

if __name__ == "__main__":
    clear()
    aranan = input("Şarkı adı veya sanatçı: ")
    ara_ve_çal(aranan)
