from mangatr import MangaTR as mangatr

manga_url = "https://manga-tr.com/manga-vinland-saga.html"  # search()'dan aldığın URL

print(mangatr.get_chapters(manga_url))
