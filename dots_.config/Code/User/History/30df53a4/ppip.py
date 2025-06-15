from fetch import animecix, openanime

search_data = animecix().fetch_anime_search_data("your name")
print(search_data)