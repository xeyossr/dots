import requests
from bs4 import BeautifulSoup

class MangaTR:
    BASE_URL = "https://manga-tr.com"

    @staticmethod
    def search(query: str) -> list[dict]:
        """
        Manga araması yapar ve sonuçları döndürür.
        Her sonuç bir dict olarak döner: {"title": ..., "url": ...}
        """
        url = f"{MangaTR.BASE_URL}/arama.html?icerik={query}"
        response = requests.get(url)
        response.raise_for_status()  # Hata oluşursa exception fırlatır

        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for a in soup.find_all("a", attrs={"data-toggle": "mangapop"}):
            title = a.get("data-original-title")
            href = a.get("href")
            if title and href:
                results.append({
                    "title": title.strip(),
                    "url": MangaTR.BASE_URL + href.strip()
                })

        return results  # Eğer sonuç yoksa boş liste döner
