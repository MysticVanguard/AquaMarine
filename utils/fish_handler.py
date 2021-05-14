from os import walk

def fetch_fish(directory:str):
    """Fetch fish given a directory."""
    fetched_fish = {
        "common": {}, 
        "uncommon": {}, 
        "rare": {},
        "epic": {},
        "legendary": {},
        "mythic": {},
    }
    
    _, _, filenames = next(walk(directory))
    for i in filenames:
        splitted = i.split("_")
        try:
            fetched_fish[splitted[0]][" ".join(splitted[2:])[:-4]] = {
                "multiplier": splitted[1],
                "name": " ".join(splitted[2:])[:-4].title(),
            }
        except KeyError:
            pass
    return fetched_fish