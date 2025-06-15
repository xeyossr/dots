from fetch import animecix, openanime

search_data = animecix().fetch_anime_search_data("blue lock")
print(search_data)