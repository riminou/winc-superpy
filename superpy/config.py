import os
import json
import logging


def init_config(configfile: str) -> bool:
    '''
    Functie voor het initialiseren van de config.
        configfile = json congfiguratie bestand
    '''
    logging.info("Initializing config...")
    if (os.path.exists(configfile)):
        try:
            with open(configfile, "r") as config_file:
                global data
                data = json.load(config_file)
                if (len(data) > 0):
                    global config_is_enabled
                    config_is_enabled = True
                    return True
                print("ERROR: Config file is empty.")
                logging.error("Config file is empty.")
        except Exception as e:
            print("ERROR: Unable to read config file.")
            logging.error("Unable to read config file.")
            print(e)
            logging.error(e)
    else:
        print("ERROR: Config file not found.")
        logging.error("Config file not found.")
    return False
