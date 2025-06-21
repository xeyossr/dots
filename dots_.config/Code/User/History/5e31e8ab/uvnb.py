import requests
from bs4 import BeautifulSoup

class MangaTR:
    BASE_URL = "https://manga-tr.com/"

    @staticmethod
    def search(query: str) -> list[dict]:
        url = f"{MangaTR.BASE_URL}/arama.html?icerik={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for a in soup.find_all("a", attrs={"data-toggle": "mangapop"}):
            title = a.get("data-original-title") #type:ignore
            href = a.get("href") #type:ignore
            if title and href:
                results.append({
                    "title": title.strip(), #type:ignore
                    "url": MangaTR.BASE_URL + href.strip() #type:ignore
                })
        return results
