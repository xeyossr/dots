from fetch import animecix, openanime

search_data = animecix().fetch_anime_search_data("your name")
#print(search_data)

def remove_movies_animecix(data):
    return [
        item for item in data
        if item.get("type") != "movie" and item.get("title_type") != "movie"
    ]


episode_data = animecix().fetch_anime_episodes("44")
print(episode_data)