import requests
from bs4 import BeautifulSoup

class MangaTR:
    BASE_URL = "https://manga-tr.com"

    @staticmethod
    def search(query: str) -> list[dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36"
        }
        url = f"{MangaTR.BASE_URL}/arama.html?icerik={query}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

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
        return results

    @staticmethod
    def get_chapters(manga_url: str) -> dict:
        """
        Manga URL'sinden tüm chapter bilgilerini döner.
        Return:
          {
            "total": int,               # Toplam chapter sayısı
            "chapters": [               # Chapter listesi
                {
                  "number": int,        # Sıralama numarası (1, 2, 3, ...)
                  "url": str,           # Chapter url (tam link)
                  "title_b": str,       # <a><b> içeriği (manga adı + chapter numarası)
                  "chapter_name": str   # div.mb1 içeriği (chapter başlığı)
                },
                ...
            ]
          }
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(manga_url, headers=headers)
        response.raise_for_status()
        
        with open("debug_chapter.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, "html.parser")
        chapters = []

        # tr class="table-bordered tbm" elemanları
        for idx, tr in enumerate(soup.find_all("tr", class_="table-bordered tbm"), 1):
            td = tr.find("td", class_="table-bordered", align="left")
            if not td:
                continue

            a = td.find("a")
            if not a:
                continue

            href = a.get("href", "").strip()
            url = MangaTR.BASE_URL + href if href else ""

            b_tag = a.find("b")
            title_b = b_tag.text.strip() if b_tag else ""

            div_mb1 = td.find("div", class_="mb1")
            chapter_name = div_mb1.text.strip() if div_mb1 else ""

            chapters.append({
                "number": idx,
                "url": url,
                "title_b": title_b,
                "chapter_name": chapter_name
            })

        return {
            "total": len(chapters),
            "chapters": chapters
        }
