from datetime import datetime
from datetime import timedelta
import superpy.config as config
import superpy.io as io


current_date_header = "current_date"


def get():
    '''
    Functie voor het ophalen van de huidige datum uit het 'current_date' bestand.
    '''
    current_date_file = config.data["files"]["current_date"]
    current_date = io.read_csv(current_date_file)
    if not current_date:
        current_date = datetime.now().strftime(config.data["date_format"])
        io.write_csv({current_date_header: current_date}, current_date_file)
    else:
        current_date = current_date[0]["current_date"]
    return current_date


def set(new_date: str):
    '''
    Functie voor het instellen van een nieuwe huidige datum.
        new_date = nieuwe datum om in te stellen
    '''
    current_date_file = config.data["files"]["current_date"]
    new_date_data = {current_date_header: new_date}
    io.write_csv(new_date_data, current_date_file, append=False)
    

def advance(days: int):
    '''
    Functie voor het vervroegen of verlaten van de huidige datum.
        days = het aantal dagen waarmee de huidige datum verlaat 
            of vervroegd dient te worden. Positieve waardes verlaten
            de huidige datum, negatieve waardes vervroegen de datum.
    '''
    try:
        days = int(days)
        current_date = get()
        if (days != 0):
            new_date = datetime.strptime(current_date, config.data["date_format"]) + timedelta(days=days)
            formatted_new_date = new_date.strftime(config.data["date_format"])
            set(formatted_new_date)
            return formatted_new_date
        return current_date
    except:
        print(f'ERROR: "{days}" is an invalid value, please enter a valid number for the amount of days.')

def reset():
    '''
    Functie voor het herstellen van de huidige
    datum naar de datum van vandaag.
    '''
    current_date = datetime.now().strftime(config.data["date_format"])
    set(current_date)


def today():
    '''
    Functie voor het ophalen van de datum van vandaag.
    '''
    return datetime.now().strftime(config.data["date_format"])