from ytmusicapi import YTMusic
import subprocess

# YTMusic başlat
ytmusic = YTMusic()

def ara_ve_çal(aranan):
    # Arama yap
    sonuçlar = ytmusic.search(aranan, filter="songs")

    if not sonuçlar:
        print("Hiç sonuç bulunamadı.")
        return

    # Sonuçları listele
    for i, şarkı in enumerate(sonuçlar[:10]):
        ad = şarkı.get("title")
        sanatçı = şarkı.get("artists", [{}])[0].get("name", "Bilinmeyen")
        süre = şarkı.get("duration", "?")
        print(f"{i+1}. {ad} - {sanatçı} [{süre}]")

    # Seçim yap
    try:
        seçim = int(input("Çalmak istediğiniz şarkının numarası: ")) - 1
        seçilen = sonuçlar[seçim]
    except (ValueError, IndexError):
        print("Geçersiz seçim.")
        return

    # YouTube videoId'si ile URL oluştur
    video_id = seçilen.get("videoId")
    if video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Şarkı çalınıyor: {url}")
        subprocess.run(["mpv", url])
    else:
        print("Video ID bulunamadı.")

# Ana fonksiyon
if __name__ == "__main__":
    aranan = input("Şarkı adı veya sanatçı: ")
    ara_ve_çal(aranan)
