import subprocess
import os
import curses
from ytmusicapi import YTMusic
import time

ytmusic = YTMusic()

def mpv_play(url):
    # mpv'yi subprocess ile başlat ve çıktıları gizle
    process = subprocess.Popen(
        ["mpv", "--no-video", "--quiet", "--input-ipc-server=/tmp/mpvsocket", url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return process

def get_current_time():
    # mpv'den şarkının mevcut zaman bilgisini almak
    try:
        process = subprocess.Popen(
            ["mpv", "--no-video", "--quiet", "--input-ipc-server=/tmp/mpvsocket", "command"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, _ = process.communicate(input="get_property time_pos\n".encode())
        return float(output.decode().strip())
    except Exception as e:
        return 0.0

def update_progress_bar(stdscr, total_duration, current_time):
    # İlerleme çubuğunu güncelle
    progress = (current_time / total_duration) * 100
    bar = f"[{'=' * int(progress / 5)}{'-' * (20 - int(progress / 5))}]"
    time_str = f"{int(current_time)}s/{int(total_duration)}s"
    stdscr.clear()
    stdscr.addstr(1, 0, f"{bar} {time_str}")
    stdscr.refresh()

def convert_duration_to_seconds(duration):
    # "4:16" gibi süreyi saniyeye çevirme
    minutes, seconds = map(int, duration.split(':'))
    return minutes * 60 + seconds

def ara_ve_çal(aranan, stdscr):
    # Şarkı araması yap
    sonuçlar = ytmusic.search(aranan, filter="songs")

    if not sonuçlar:
        stdscr.addstr(3, 0, "Hiç sonuç bulunamadı.")
        stdscr.refresh()
        time.sleep(2)
        return

    # Kullanıcıya şarkı listesini sun
    for i, şarkı in enumerate(sonuçlar[:10]):
        ad = şarkı.get("title")
        sanatçı = şarkı.get("artists", [{}])[0].get("name", "Bilinmeyen")
        süre = şarkı.get("duration", "?")
        stdscr.addstr(3 + i, 0, f"{i+1}. {ad} - {sanatçı} [{süre}]")
    stdscr.refresh()

    try:
        # Kullanıcıdan şarkı seçmesini iste
        seçim = int(stdscr.getstr(14, 0, 3)) - 1
        seçilen = sonuçlar[seçim]
    except (ValueError, IndexError):
        stdscr.addstr(3, 0, "Geçersiz seçim.")
        stdscr.refresh()
        time.sleep(2)
        return

    video_id = seçilen.get("videoId")
    if video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"
        stdscr.addstr(3, 0, f"Şarkı çalınıyor...      ")
        stdscr.refresh()

        # mpv'yi başlat ve kontrol et
        process = mpv_play(url)

        duration = seçilen.get("duration", "0:00")
        total_duration = convert_duration_to_seconds(duration)  # Süreyi saniyeye çevir
        current_time = 0.0

        while current_time < total_duration:
            current_time = get_current_time()
            update_progress_bar(stdscr, total_duration, current_time)
            time.sleep(0.1)

            key = stdscr.getch()  # Kullanıcıdan tuş girişi al
            if key == ord('q'):  # 'q' tuşu ile çıkış
                break
            elif key == 259:  # yukarı ok tuşu (geri sarma: 5 saniye)
                current_time = max(current_time - 5, 0)
            elif key == 258:  # aşağı ok tuşu (ileri sarma: 5 saniye)
                current_time = min(current_time + 5, total_duration)

        process.terminate()

    else:
        stdscr.addstr(3, 0, "Video ID bulunamadı.")
        stdscr.refresh()
        time.sleep(2)

def main(stdscr):
    os.system("clear")  # Terminali temizle
    aranan = stdscr.getstr(0, 0, 20).decode("utf-8")  # Kullanıcıdan şarkı adı veya sanatçı adı al
    ara_ve_çal(aranan, stdscr)  # Şarkıyı ara ve çal

if __name__ == "__main__":
    curses.wrapper(main)
