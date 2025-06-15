from fetch import animecix, openanime

search_data = animecix().fetch_anime_search_data("your name")
#print(search_data)

episode_data = animecix().fetch_anime_episodes(11)
print(episode_data)