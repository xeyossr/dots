from modules.fetch import animecix

class animecix:
    def __init__(self):
        self.fetcher = animecix()

    def queryLoop(self, query=None):
        return self.fetcher.queryLoop(query)

    def fetch_anime_episodes(self, anime_id):
        return self.fetcher.fetch_anime_episodes(anime_id)

    def fetch_anime_watch_api_url(self, episode_url):
        return self.fetcher.fetch_anime_watch_api_url(episode_url)

    def fetch_anime_watch_api_url_movie(self, anime_id):
        return self.fetcher.fetch_anime_watch_api_url_movie(anime_id)

    def fetch_all(self, anime_id, episode_url=None):
        """
        fetch_anime_episodes, fetch_anime_watch_api_url (isteğe bağlı),
        ve fetch_anime_watch_api_url_movie çıktılarının hepsini döndürür.
        """
        result = {
            "episodes": self.fetch_anime_episodes(anime_id),
            "movie_url": self.fetch_anime_watch_api_url_movie(anime_id)
        }

        if episode_url:
            result["watch_urls"] = self.fetch_anime_watch_api_url(episode_url)
        else:
            result["watch_urls"] = None

        return result


class openanime:
    def __init__(self):
        pass  # Henüz yazılmadı

    def placeholder(self):
        return "Henüz desteklenmiyor"
