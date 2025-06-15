from ytmusicapi import YTMusic
import subprocess

ytmusic = YTMusic()

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
        subprocess.run(
            ["mpv", "--no-video", "--osc", "--vo=null", "--really-quiet", "--audio-display=visualizer", url],
            stdout=subprocess.DEVNULL,
            #stderr=subprocess.DEVNULL
        )
    else:
        print("Video ID bulunamadı.")

if __name__ == "__main__":
    aranan = input("Şarkı adı veya sanatçı: ")
    ara_ve_çal(aranan)
