def read_config():
    config = {}
    with open("config.txt", "r") as config_file:
        lines = [line.strip() for line in config_file.readlines()]

        for line in lines:
            key, value = line.split("=")[0], "=".join(line.split("=")[1:])
            config[key] = value

    return config
