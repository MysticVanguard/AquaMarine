from os import walk

def fetch_fish(dir:str) -> dict:
    """Fetch fish given a directory."""
    fetched_fish = {
        "common": [], 
        "uncommon": [], 
        "rare": [],
        "epic": [],
        "legendary": [],
        "mythic": [],
    }
    
    _, _, filenames = next(walk(dir))
    for i in filenames:
        splitted = i.split("_")
        try:
            fetched_fish[splitted[0]].append(" ".join(splitted[1:]).title())
        except KeyError:
            pass
    return fetched_fish
