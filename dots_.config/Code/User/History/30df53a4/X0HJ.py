from fetch import animecix, openanime

def remove_movies_animecix(data):
    return [
        item for item in data
        if item.get("type") != "movie" and item.get("title_type") != "movie"
    ]

def get_search_data(source, query):
    if source.lower() == "animecix":
        return remove_movies_animecix(animecix().fetch_anime_search_data(query))
    elif source.lower() == "openanime":
        return openanime().search(query)

print(get_search_data("animecix", "blue lock"))
print("\n")
print(get_search_data("openanime", "blue lock"))

#episode_data = animecix().fetch_anime_episodes("44")
#print(episode_data)