import time, requests
from urllib.parse import urlparse, parse_qs

class animecix:
    def __init__(self):
        self.base_url = "https://anm.cx/"
        self.video_players = ["tau-video.xyz", "sibnet"]
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }

    def _get_json(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def fetch_anime_search_data(self, query):
        search_url = f"{self.base_url}secure/search/{query}?type=&limit=20"
        data = self._get_json(search_url)
        if data and 'results' in data:
            return [
                {
                    'name': item.get('name'),
                    'id': item.get('id'),
                    'type': item.get('type'),
                    'title_type': item.get("title_type"),
                    'original_title': item.get("original_title")
                }
                for item in data['results']
            ]
        return []

    def fetch_anime_seasons(self, selected_id):
        url = f"https://mangacix.net/secure/related-videos?episode=1&season=1&titleId={selected_id}&videoId=637113"
        json_data = self._get_json(url)
        if json_data and "videos" in json_data:
            videos = json_data["videos"]
            if videos:
                seasons = videos[0].get('title', {}).get('seasons', [])
                if isinstance(seasons, list):
                    return list(range(len(seasons)))
        return []

    def fetch_anime_episodes(self, selected_id):
        seasons = self.fetch_anime_seasons(selected_id)
        episodes = []
        seen_episode_names = set()
        for season_index in seasons:
            url = f"https://mangacix.net/secure/related-videos?episode=1&season={season_index + 1}&titleId={selected_id}&videoId=637113"
            data = self._get_json(url)
            if data and 'videos' in data:
                for item in data['videos']:
                    name = item.get('name', "No name field")
                    if name not in seen_episode_names:
                        episode_url = item.get('url', 'No url field')
                        episodes.append({'name': name, 'url': episode_url})
                        seen_episode_names.add(name)
        return episodes

    def fetch_anime_watch_api_url(self, url):
        wtch_url = f"{self.base_url}{url}"
        try:
            response = requests.get(wtch_url, headers=self.headers, allow_redirects=True)
            response.raise_for_status()
            time.sleep(3)
            final_resp = response.url
            path = urlparse(final_resp).path
            embed_id = path.split('/')[2]
            query = urlparse(final_resp).query
            vid = parse_qs(query).get('vid', [None])[0]
            api_url = f"https://{self.video_players[0]}/api/video/{embed_id}?vid={vid}"
            wtch_resp = requests.get(api_url)
            wtch_resp.raise_for_status()
            return [{'label': item.get('label', 'No Label field'), 'url': item.get('url', 'No URL field')} for item in wtch_resp.json().get('urls', [])]
        except requests.RequestException:
            return []

    def fetch_anime_watch_api_url_movie(self, selected_id):
        url = f"https://mangacix.net/secure/titles/{selected_id}"
        json_dt = self._get_json(url)
        if not json_dt:
            return None
        url_vid = json_dt.get("title", {}).get("videos", [{}])[0].get("url")
        if not url_vid:
            return None
        try:
            path = urlparse(url_vid).path
            embed_id = path.split("/")[2]
            api_url = f"https://{self.video_players[0]}/api/video/{embed_id}"
            time.sleep(5)
            video_data = self._get_json(api_url)
            if not video_data:
                return None
            for quality in ["1080p", "720p", "480p"]:
                for url_info in video_data.get('urls', []):
                    if url_info.get("label") == quality:
                        return url_info.get("url")
        except Exception:
            if self.video_players[1] in url_vid:
                return url_vid + ".mp4"
        return None

    def fetch_tr_caption_url(self, episode, season, selected_id):
        """
        Belirtilen bölüm/sezon/id için TR altyazı url'sini getirir.
        """
        url = f"https://mangacix.net/secure/related-videos?episode={episode}&season={season}&titleId={selected_id}&videoId=637113"
        json_data = self._get_json(url)
        if not json_data or "videos" not in json_data:
            return None

        for video in json_data["videos"]:
            captions = video.get("captions")
            if not captions or not isinstance(captions, list):
                continue

            # TR dilinde olan varsa
            for caption in captions:
                lang = caption.get("language", "").lower()
                if lang == "tr":
                    return caption.get("url")

            # TR yoksa ilk caption'ın url'si
            if captions:
                return captions[0].get("url")

        return None

class openanime:
    def __init__(self):
        self.base_url = "https://api.openani.me"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "origin": "https://openani.me",
            "Referer": "https://openani.me",
            "Accept": "application/json",
        }

    def get_json(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Veri alınırken hata oluştu: {e}")
            return None

    def search(self, query):
        """Anime araması yapar"""
        url = f"{self.base_url}/anime/search?q={query}"
        data = self.get_json(url)
        if data:
            return [{'name': anime.get('english'), 'slug': anime.get('slug')} for anime in data]
        return []

    def get_seasons(self, slug):
        """Slug ile sezon sayısı ve malID getirir"""
        url = f"{self.base_url}/anime/{slug}"
        data = self.get_json(url)
        if data:
            return {
                "number_of_seasons": data.get("numberOfSeasons", 0),
                "mal_id": data.get("malID"),
                "type": data.get("type")
            }
        return {}

    def get_episodes(self, slug):
        """Tüm sezonlardaki tüm bölümleri sırayla getirir"""
        season_info = self.get_seasons(slug)
        season_count = season_info.get("number_of_seasons", 0)
        if not season_count:
            return []

        all_episodes = []
        for season in range(1, season_count + 1):
            url = f"{self.base_url}/anime/{slug}/season/{season}"
            data = self.get_json(url)
            if data:
                episodes = data.get("season", {}).get("episodes", [])
                season_number = data["season"]["season_number"]
                for episode in episodes:
                    all_episodes.append({
                        "name": episode.get("name"),
                        "episode": episode.get("episodeNumber"),
                        "season": season_number
                    })
        return sorted(all_episodes, key=lambda ep: (ep["season"], ep["episode"]))

    def get_stream_url(self, slug, episode_number, season_number):
        """Bölüm izleme bağlantısı döndürür"""
        url = f"{self.base_url}/anime/{slug}/season/{season_number}/episode/{episode_number}"
        data = self.get_json(url)
        if data and "episodeData" in data:
            for index in range(3, -1, -1):
                try:
                    return data["episodeData"]["files"][index]["file"]
                except (IndexError, KeyError):
                    continue
        return None
