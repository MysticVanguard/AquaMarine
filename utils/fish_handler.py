from utils.load_config import config
from os import walk

def fetch_fish(directory:str=config["assets"]["images"]["fish"]):
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
            fetched_fish[splitted[0]][fish_name] = {
                "rarity": splitted[0],
                "cost": int(splitted[1]),
                "raw_name": "_".join(splitted[2:])[:-4],
                "name": fish_name.title(),
                "image": f"{directory}/{i}"
            }
            
        except KeyError:
            pass

   
    return fetched_fish
    

def make_golden(fish:dict):
    fish["raw_name"] = f"golden_{fish['raw_name']}"
    fish["name"] = f"Golden {fish['name']}"
    fish["image"] = fish["image"][:16] + "golden_" + fish["image"][16:]
    return fish

def make_inverted(fish:dict):
    fish["raw_name"] = f"inverted_{fish['raw_name']}"
    fish["name"] = f"Inverted {fish['name']}"
    fish["image"] = fish["image"][:16] + "inverted_" + fish["image"][16:]
    return fish