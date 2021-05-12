from os import walk

def fetch_fish(dir:str) -> dict:
    """Fetch fish given a directory."""
    fetched_fish = {
        "common": {}, 
        "uncommon": {}, 
        "rare": {},
        "epic": {},
        "legendary": {},
        "mythic": {},
    }
    
    _, _, filenames = next(walk(dir))
    for i in filenames:
        splitted = i.split("_")
        try:
            fetched_fish[splitted[0]][splitted[2:]] = {
                "multiplier": splitted[1],
                "name": " ".join(splitted[2:]).title(),
            }
        except KeyError:
            pass
    return fetched_fish
