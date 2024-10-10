import datetime

import superpy.config as config


def price(price: float):
    '''
    Functie voor het valideren van de opgegeven prijs.
        price = de prijs om te valideren
    '''
    if (price >= 0):
        return True
    else:
        print("ERROR: A negative price was given, only prices of 0 or higher are allowed.")
    return False


def date_format(date: str):
    '''
    Functie voor het valideren van de datum format.
        date = de datum om te valideren volgens DATE_FORMAT
    '''
    try:
        date_parts = len(date.split("-"))
        date_format_parts = config.data["date_format"].split("-")
        date_format = "-".join(date_format_parts[0:date_parts])
        datetime.datetime.strptime(date, date_format)
    except ValueError:
        print(f"ERROR: Invalid date format, use the '{config.data['date_format']}' format." )
        return False
    return True


def expiration_date(current_date: str,
                    expiration_date: str):
    '''
    Functie voor het valideren van de vervaldatum.
        current_date = huidige datum
        expiration_date = vervaldatum
    '''
    if date_format(current_date) and date_format(expiration_date):
       parsed_current_date = datetime.datetime.strptime(current_date, config.data["date_format"])
       parsed_expiration_date = datetime.datetime.strptime(expiration_date, config.data["date_format"])
       if parsed_expiration_date >= parsed_current_date:
           return True
       print("ERROR: Expiration date cannot be earlier then the superpy current date.")
    return False


def quantity(quantity: int):
    '''
    Functie voor het valideren van het aantal.
        quantity = het aantal
    '''
    if quantity != 0:
        return True
    print("ERROR: Quantity cannot be '0'")
    return False
