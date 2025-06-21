from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class MangaTR:
    BASE_URL = "https://manga-tr.com"

    @staticmethod
    def get_chapters_selenium(manga_url: str) -> dict:
        """
        Selenium ile manga sayfasını açıp JS sonrası chapter listesini çeker.
        """
        options = Options()
        options.add_argument("--headless")  # Tarayıcı arayüzü olmadan çalışır
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(manga_url)

        try:
            # Chapterlerin yüklendiği tabloyu bekle (örnek: tr'ler içinde)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr.table-bordered.tbm"))
            )
        except Exception as e:
            driver.quit()
            raise RuntimeError(f"Chapter listesi yüklenemedi veya bulunamadı: {e}")

        chapters = []
        tr_elements = driver.find_elements(By.CSS_SELECTOR, "tr.table-bordered.tbm")

        for idx, tr in enumerate(tr_elements, 1):
            try:
                td = tr.find_element(By.CSS_SELECTOR, "td.table-bordered[align='left']")
                a = td.find_element(By.TAG_NAME, "a")
                href = a.get_attribute("href")
                b_tag = a.find_element(By.TAG_NAME, "b")
                title_b = b_tag.text.strip()
                div_mb1 = td.find_element(By.CLASS_NAME, "mb1")
                chapter_name = div_mb1.text.strip()
                chapters.append({
                    "number": idx,
                    "url": href,
                    "title_b": title_b,
                    "chapter_name": chapter_name
                })
            except Exception:
                # Eğer beklenen element bulunmazsa o satırı atla
                continue

        driver.quit()

        return {
            "total": len(chapters),
            "chapters": chapters
        }
