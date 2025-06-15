#!/usr/bin/env python3

from modules.fetch import animecix, openanime
from pypresence import Client
import modules.player as player
import modules.ui as ui

from dotenv import load_dotenv
import subprocess, argparse, time, json, sys, os, re

load_dotenv(os.path.expanduser("~/.config/anitr-cli/config"))
default_ui = os.getenv("DEFAULT_UI", "tui")
discord_rpc = os.getenv("DISCORD_RPC", "Enabled")
sources = ["AnimeciX (anm.cx)", "OpenAnime (openani.me)"]

rpc = None
start_time = int(time.time())

def log_anime_details(details: str, state: str, large_text: str, source: str, source_url: str, path: str = "/tmp/anime_details"):
    data = {
        "details": f"Watching {details}",
        "state": state,
        "large_image": "anitrcli",
        "large_text": large_text,
        "small_image": source.lower(),
        "small_text": source,
        "buttons": [
            { "label": source, "url": source_url },
            { "label": "GitHub", "url": "https://github.com/xeyossr/anitr-cli" }
        ]
    }
    
    with open(path, "w", encoding="utf-8") as tmpf:
        json.dump(data, tmpf, indent=2, ensure_ascii=False)

def start_discord_rpc(client_id="1383421771159572600", filepath="/tmp/anime_details"):
    global rpc
    if rpc is None:
        rpc = Client(client_id)
        rpc.start()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    activity = {
        "pid": os.getpid(),
        "activity": {
            "type": 3,
            "details": data.get("details"),
            "state": data.get("state"),
            "timestamps": {
                "start": start_time
            },
            "assets": {
                "large_image": data.get("large_image"),
                "large_text": data.get("large_text"),
                "small_image": data.get("small_image"),
                "small_text": data.get("small_text")
            },
            "buttons": data.get("buttons", [])
        }
    }

    rpc.send_data(1, {
        "cmd": "SET_ACTIVITY",
        "args": activity,
        "nonce": "watching-anime"
    })


def update_discord_rpc(filepath="/tmp/anime_details"):
    global rpc
    if rpc is None:
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    activity = {
        "pid": os.getpid(),
        "activity": {
            "type": 3,
            "details": data.get("details"),
            "state": data.get("state"),
            "timestamps": {
                "start": start_time
            },
            "assets": {
                "large_image": data.get("large_image"),
                "large_text": data.get("large_text"),
                "small_image": data.get("small_image"),
                "small_text": data.get("small_text")
            },
            "buttons": data.get("buttons", [])
        }
    }

    rpc.send_data(1, {
        "cmd": "SET_ACTIVITY",
        "args": activity,
        "nonce": "watching-anime"
    })

def stop_discord_rpc():
    global rpc
    if rpc:
        rpc.clear_activity()
        rpc.close()
        rpc = None

def print_smart(text: str, notification_msg: str, notification: bool = True):
    if default_ui == "rofi":
        if notification:
            send_notification("anitr-cli", notification_msg)
    else:
        print(text)

def send_notification(title, message):
    subprocess.run(['notify-send', '-a', title, message])

def get_source() -> str:
    return ui.select_menu(default_ui, sources, "Kaynak seç:", False)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="💫 Terminalden anime izlemek için CLI aracı.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Kaynak seçimi
    parser.add_argument(
        "--source",
        choices=["AnimeciX", "OpenAnime"],
        type=str,
        help="Hangi kaynak ile anime izlemek istediğinizi belirtir."
    )

    # Discord RPC
    parser.add_argument(
        "--disable-rpc",
        action="store_true",
        help="Discord Rich Presence özelliğini devre dışı bırakır."
    )

    # Arayüz seçenekleri
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument(
        "--rofi",
        action="store_true",
        help="Uygulamanın arayüzünü rofi ile açar."
    )
    mode_group.add_argument(
        "--tui",
        action="store_true",
        help="Terminalde TUI arayüzü ile açar."
    )

    # Güncelleme seçeneği
    parser.add_argument(
        "--update",
        action="store_true",
        help="anitr-cli aracını en son sürüme günceller."
    )

    return parser.parse_args()

def AnimeciX():    
    query = ui.search_menu(default_ui, "Anime ara >")
    
    if not query or query == "Çık":
        return

    search_data = animecix().fetch_anime_search_data(query)
    
    anime_data = [{"name": item["name"], "id": item["id"], "title_type": item.get("title_type", ""), "type": item.get("type", "")} for item in search_data]
    anime_names = [f'{item["name"]} (ID: {item["id"]})' for item in anime_data]
    anime_types = [
        "movie" if (item["title_type"] and item["title_type"].lower() == "movie") or 
                    (item["type"] and item["type"].lower() == "movie") else "tv"
        for item in anime_data
    ]

    selected_anime_name = ui.select_menu(default_ui, anime_names, "Anime seç:", True)
    if not selected_anime_name:
        return

    selected_anime_index = anime_names.index(selected_anime_name)
    selected_anime_type = anime_types[selected_anime_index]
    is_movie = selected_anime_type == "movie"
    
    match = re.match(r'(.+) \(ID: (\d+)\)', selected_anime_name)
    if match:
        selected_anime_name = match.group(1)
        selected_anime_id = match.group(2)

    selected_index, selected_label = None, None 
    selected_resolution_index = 0  
    selected_resolution = None 

    def update_watch_api(index, selected_id):
        if is_movie:
            data = animecix().fetch_anime_movie_watch_api_url(selected_id)
            # Movie verisi: {'video_streams': [{'label': '480p', 'url': '...'}, ...]}
            data = data.get("video_streams", []) # type: ignore
            
            caption_url = None
            for stream in data:
                if "caption_url" in stream:
                    caption_url = stream["caption_url"]
                    break

        else:
            data = animecix().fetch_anime_watch_api_url(anime_episodes_data[index]["url"])
            # Dizi verisi: [{'label': '1080p', 'url': '...'}, ...]

            caption_url = animecix().fetch_tr_caption_url(selected_season_index, selected_episode_index, selected_anime_id)

        try:
            data.sort(key=lambda x: int(x['label'][:-1]), reverse=True)
        except Exception:
            pass

        labels = [item['label'] for item in data]
        urls = [item['url'] for item in data]
        return data, labels, urls, caption_url


    if not is_movie:
        anime_episodes_data = animecix().fetch_anime_episodes(selected_anime_id)
        anime_episode_names = [item['name'] for item in anime_episodes_data]
        selected_episode_index = 0
        total_episodes = len(anime_episode_names)
        selected_episode_name = anime_episode_names[selected_episode_index]
        selected_season_index = anime_episodes_data[selected_episode_index]["season_num"] - 1
    else:
        selected_episode_index = 0
        total_episodes = 1 
        selected_episode_name = selected_anime_name 
        selected_season_index = 0


    anime_series_menu_options = (
        ["Filmi izle", "Çözünürlük seç", "Anime ara", "Çık"] if is_movie else
        ["İzle", "Sonraki bölüm", "Önceki bölüm", "Bölüm seç", "Çözünürlük seç", "Anime ara", "Çık"]
    )
    
    while True:
        if selected_resolution:
            if not is_movie:
                menu_header = (f"\033[33mOynatılıyor\033[0m: {selected_anime_name} ({selected_resolution}) |"
                               f" {selected_episode_index + 1}/{total_episodes}"
                               if selected_anime_name else "")
            elif is_movie:
                menu_header = (f"\033[33mOynatılıyor\033[0m: {selected_anime_name} ({selected_resolution})"
                               if selected_anime_name else "")
        
        else:
            if not is_movie:
                menu_header = (f"\033[33mOynatılıyor\033[0m: {selected_anime_name} |"
                               f" {selected_episode_index + 1}/{total_episodes}"
                               if selected_anime_name else "")
            elif is_movie:
                menu_header = (f"\033[33mOynatılıyor\033[0m: {selected_anime_name}"
                               if selected_anime_name else "")

        print_smart(menu_header, "", False)

        log_anime_details(
            details=f"{selected_anime_name}",
            state=f"{selected_episode_name} ({selected_episode_index + 1}/{total_episodes})" if not is_movie else f"{selected_anime_name}",
            large_text=f"{selected_anime_name}",
            source="AnimeciX",
            source_url="https://anm.cx"
        )
        
        if discord_rpc.lower() == "enabled":
            start_discord_rpc()

        selected_option = ui.select_menu(default_ui, anime_series_menu_options, "", False, menu_header)

        if selected_option == "İzle" or selected_option == "Filmi izle":
            watch_api_data, watch_api_labels, watch_api_urls, subtitle_url = update_watch_api(selected_episode_index, selected_anime_id)

            if selected_resolution is None:
                if watch_api_labels:
                    selected_index, selected_label = max(
                        enumerate(watch_api_labels), key=lambda x: int(x[1][:-1])
                    )
                    selected_resolution = selected_label 
                    selected_resolution_index = selected_index
                else:
                    selected_resolution_index = 0

            while selected_resolution_index >= len(watch_api_urls):
                selected_resolution_index -= 1

            if not is_movie:
                print_smart(
                    f"\033[33mOynatılıyor\033[0m: {selected_episode_name}", 
                    f"{selected_anime_name}, {selected_episode_name} ({selected_episode_index+1}/{total_episodes}) oynatılıyor"
                )
            elif is_movie:
                print_smart(
                    f"\033[33mOynatılıyor\033[0m: {selected_anime_name}", 
                    f"{selected_anime_name} oynatılıyor"
                )

            selected_season_index = anime_episodes_data[selected_episode_index]["season_num"] - 1 if not is_movie else 0
            watch_url = watch_api_urls[selected_resolution_index]

            player.open_with_video_player(watch_url, subtitle_url)
            continue

        elif selected_option == "Sonraki bölüm":
            if selected_episode_index + 1 >= len(anime_episodes_data):
                ui.show_error(default_ui, "Zaten son bölümdesiniz.")
                continue
            selected_episode_index += 1
            selected_episode_name = anime_episode_names[selected_episode_index]

            log_anime_details(
                details=f"{selected_anime_name}",
                state=f"{selected_episode_name} ({selected_episode_index + 1}/{total_episodes})" if not is_movie else f"{selected_anime_name}",
                large_text=f"{selected_anime_name}",
                source="AnimeciX",
                source_url="https://anm.cx"
            )

            update_discord_rpc()

            continue

        elif selected_option == "Önceki bölüm":
            if selected_episode_index == 0:
                ui.show_error(default_ui, "Zaten ilk bölümdesiniz.")
                continue
            selected_episode_index -= 1
            selected_episode_name = anime_episode_names[selected_episode_index]

            log_anime_details(
                details=f"{selected_anime_name}",
                state=f"{selected_episode_name} ({selected_episode_index + 1}/{total_episodes})" if not is_movie else f"{selected_anime_name}",
                large_text=f"{selected_anime_name}",
                source="AnimeciX",
                source_url="https://anm.cx"
            )

            update_discord_rpc()

            continue

        elif selected_option == "Bölüm seç":
            selected_episode_name = ui.select_menu(default_ui, anime_episode_names, "Bölüm seç:", True)

            if not selected_episode_name:
                continue

            selected_episode_index = anime_episode_names.index(selected_episode_name)
            selected_episode_name = anime_episode_names[selected_episode_index]

            log_anime_details(
                details=f"{selected_anime_name}",
                state=f"{selected_episode_name} ({selected_episode_index + 1}/{total_episodes})" if not is_movie else f"{selected_anime_name}",
                large_text=f"{selected_anime_name}",
                source="AnimeciX",
                source_url="https://anm.cx"
            )

            update_discord_rpc()

            continue
        
        elif selected_option == "Çözünürlük seç":
            watch_api_data, watch_api_labels, watch_api_urls, subtitle_url = update_watch_api(selected_episode_index, selected_anime_id)
            selected_resolution = ui.select_menu(default_ui, watch_api_labels, "Çözünürlük seç:", False)

            if not selected_resolution:
                continue

            selected_resolution_index = watch_api_labels.index(selected_resolution)
        
        elif selected_option == "Anime ara":
            AnimeciX()
            continue

        elif selected_option == "Çık":
            sys.exit()

def OpenAnime():    
    query = ui.search_menu(default_ui, "Anime ara >")
    if not query or query == "Çık":
        return
    
    search_data = openanime().search(query)
    
    anime_names = [f'{item["name"]} (ID: {item["slug"]})' for item in search_data]

    selected_anime_name = ui.select_menu(default_ui, anime_names, "Anime seç:", True)
    
    if not selected_anime_name:
        return
    
    match = re.match(r'(.+) \(ID: (.+)\)', selected_anime_name)
    if match:
        selected_anime_name = match.group(1)
        selected_anime_slug = match.group(2)

    selected_index, selected_label = None, None 
    selected_resolution_index = 0  
    selected_resolution = None 

    seasons_data = openanime().get_seasons(selected_anime_slug)
    anime_type = seasons_data.get("type", "").lower()
    is_movie = anime_type == "movie"

    anime_episodes_data = openanime().get_episodes(selected_anime_slug, is_movie)

    anime_episode_names = []
    for item in anime_episodes_data:
        if is_movie:
            anime_episode_names.append(selected_anime_name)
        else:
            season = item['season']
            episode = item['episode']
            if season == 1:
                anime_episode_names.append(f"{episode}. Bölüm")
            else:
                anime_episode_names.append(f"{season}. Sezon, {episode}. Bölüm")

    if not anime_episodes_data:
        ui.show_error(default_ui, "Bu animeye ait bölüm bulunamadı.")
        return

    selected_episode_index = 0
    total_episodes = len(anime_episode_names)
    selected_episode_name = anime_episode_names[selected_episode_index]
    

    anime_series_menu_options = (
        ["Filmi izle", "Çözünürlük seç", "Anime ara", "Çık"] if is_movie else
        ["İzle", "Sonraki bölüm", "Önceki bölüm", "Bölüm seç", "Çözünürlük seç", "Anime ara", "Çık"]
    )

    def update_watch_api(index):
        episode_data = anime_episodes_data[index]
        data = openanime().get_stream_url(selected_anime_slug, episode_data["episode"], episode_data["season"])
        if not data:
            return [], [], []
        
        data.sort(key=lambda x: int(x['resolution']), reverse=True)
        labels = [f"{item['resolution']}p" for item in data]
        urls = [item['url'] for item in data]
        return data, labels, urls

    while True:
        if selected_resolution:
            menu_header = (f"\033[33mOynatılıyor\033[0m: {selected_anime_name} ({selected_resolution}) |"
                           f" {selected_episode_index + 1}/{total_episodes}"
                           if selected_anime_name else "")
        else:
            menu_header = (f"\033[33mOynatılıyor\033[0m: {selected_anime_name} |"
                           f" {selected_episode_index + 1}/{total_episodes}"
                           if selected_anime_name else "")

        print_smart(menu_header, "", False)
        
        log_anime_details(
            details=f"{selected_anime_name}",
            state=f"{selected_episode_name} ({selected_episode_index + 1}/{total_episodes})" if not is_movie else f"{selected_anime_name}",
            large_text=f"{selected_anime_name}",
            source="OpenAnime",
            source_url="https://openani.me"
        )
        
        if discord_rpc.lower() == "enabled":
            start_discord_rpc()
        
        selected_option = ui.select_menu(default_ui, anime_series_menu_options, "", False, menu_header)

        if selected_option in ["İzle", "Filmi izle"]:
            watch_api_data, watch_api_labels, watch_api_urls = update_watch_api(selected_episode_index)

            if not watch_api_labels:
                ui.show_error(default_ui, "Çözünürlük verisi alınamadı.")
                continue

            if selected_resolution is None:
                selected_index, selected_label = max(
                    enumerate(watch_api_labels), key=lambda x: int(x[1][:-1])
                )
                selected_resolution = selected_label 
                selected_resolution_index = selected_index

            while selected_resolution_index >= len(watch_api_urls):
                selected_resolution_index -= 1

            print_smart(
                f"\033[33mOynatılıyor\033[0m: {selected_episode_name}",
                f"{selected_anime_name}, {selected_episode_name} ({selected_episode_index+1}/{total_episodes}) oynatılıyor"
            )

            raw_video_url = watch_api_urls[selected_resolution_index]
            season_for_url = 1 if is_movie else anime_episodes_data[selected_episode_index]["season"]
            watch_url = f"{openanime().player}/animes/{selected_anime_slug}/{season_for_url}/{raw_video_url}"
            subtitle_url = None
            player.open_with_video_player(watch_url, subtitle_url)
            continue

        elif selected_option == "Sonraki bölüm":
            if selected_episode_index + 1 >= len(anime_episodes_data):
                ui.show_error(default_ui, "Zaten son bölümdesiniz.")
                continue
            selected_episode_index += 1
            selected_episode_name = anime_episode_names[selected_episode_index]

            log_anime_details(
                details=f"{selected_anime_name}",
                state=f"{selected_episode_name} ({selected_episode_index + 1}/{total_episodes})" if not is_movie else f"{selected_anime_name}",
                large_text=f"{selected_anime_name}",
                source="AnimeciX",
                source_url="https://anm.cx"
            )

            update_discord_rpc()

            continue

        elif selected_option == "Önceki bölüm":
            if selected_episode_index == 0:
                ui.show_error(default_ui, "Zaten ilk bölümdesiniz.")
                continue
            selected_episode_index -= 1
            selected_episode_name = anime_episode_names[selected_episode_index]

            log_anime_details(
                details=f"{selected_anime_name}",
                state=f"{selected_episode_name} ({selected_episode_index + 1}/{total_episodes})" if not is_movie else f"{selected_anime_name}",
                large_text=f"{selected_anime_name}",
                source="AnimeciX",
                source_url="https://anm.cx"
            )

            update_discord_rpc()

            continue

        elif selected_option == "Bölüm seç":
            selected_episode_name = ui.select_menu(default_ui, anime_episode_names, "Bölüm seç:", True)

            if not selected_episode_name:
                continue

            selected_episode_index = anime_episode_names.index(selected_episode_name)

            log_anime_details(
                details=f"{selected_anime_name}",
                state=f"{selected_episode_name} ({selected_episode_index + 1}/{total_episodes})" if not is_movie else f"{selected_anime_name}",
                large_text=f"{selected_anime_name}",
                source="AnimeciX",
                source_url="https://anm.cx"
            )

            update_discord_rpc()

            continue

        elif selected_option == "Çözünürlük seç":
            watch_api_data, watch_api_labels, watch_api_urls = update_watch_api(selected_episode_index)
            selected_resolution = ui.select_menu(default_ui, watch_api_labels, "Çözünürlük seç:", False)

            if not selected_resolution:
                continue

            selected_resolution_index = watch_api_labels.index(selected_resolution)
        
        elif selected_option == "Anime ara":
            OpenAnime()
            continue

        elif selected_option == "Çık":
            sys.exit()

def main():
    import modules.update as update
    
    global default_ui
    args = parse_arguments()

    if not args.update:
        if update.check_update_notice():
            send_notification("anitr-cli", update.check_update_notice())
    
    if args.rofi:
        default_ui = "rofi"
    elif args.tui:
        default_ui = "tui"
    elif args.update:
        from packaging import version

        latest = update.get_latest_version()
        if version.parse(latest) > version.parse(update.CURRENT_VERSION):
            print(f"Yeni sürüm bulundu: \033[31mv{update.CURRENT_VERSION}\033[0m → \033[32mv{latest}\033[0m")
            update.download_and_replace_binary()
        else:
            print("Zaten en güncel sürümdesiniz.")
        sys.exit()
    
    if args.disable_rpc:
        global discord_rpc
        discord_rpc = "Disabled"

    if args.source.lower() == "openanime":
        OpenAnime()
    elif args.source.lower() == "animecix":
        AnimeciX()
    else:
        print(f"\033[32m[!] - Geçersiz kaynak\033[0m")
        sys.exit(1)

    selected_source = get_source()
    if selected_source == "AnimeciX (anm.cx)":
        AnimeciX()
    elif selected_source == "OpenAnime (openani.me)":
        OpenAnime()
    else:
        return

if __name__ == "__main__":
    main()
