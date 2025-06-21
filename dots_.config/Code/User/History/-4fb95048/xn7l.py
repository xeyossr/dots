from mangatr import MangaTR

manga_url = "https://manga-tr.com/manga-vinland-saga.html"  # search()'dan aldığın URL
chapters_info = MangaTR.get_chapters(manga_url)

print(f"Toplam chapter: {chapters_info['total']}")
for ch in chapters_info['chapters']:
    print(f"{ch['number']}. {ch['title_b']} - {ch['chapter_name']} -> {ch['url']}")
