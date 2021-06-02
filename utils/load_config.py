import toml


with open("./config/config.toml") as f:
    config = toml.loads(f.read())
