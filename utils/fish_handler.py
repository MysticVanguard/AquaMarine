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
        if splitted[0] in ['inverted','golden']:
            continue
        
        try:
            fish_name = " ".join(splitted[2:])[:-4]
            fetched_fish[fish_name] = {
                "multiplier": splitted[1],
                "name": fish_name.title(),
                "image": f"./assets/images/{i}"
            }
            
        except KeyError:
            pass
        
    return fetched_fish

def make_golden(fish:dict):
    fish["name"] = f"Golden {fish['name']}"
    fish["image"] = fish["image"][:16] + "golden_" + fish["image"][16:]

def make_inverted(fish:dict):
    fish["name"] = f"Inverted {fish['name']}"
    fish["image"] = fish["image"][:16] + "inverted_" + fish["image"][16:]