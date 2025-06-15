import subprocess, time

def open_with_video_player(url, subtitle_url=None):
    """Video Oynatıcı"""
    try:
        cmd = ['mpv', '--fullscreen']
        if subtitle_url:
            cmd += ['--sub-file=' + subtitle_url]
        cmd.append(url)

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Oynatılırken Hata Oluştu!", e)
        time.sleep(10)
