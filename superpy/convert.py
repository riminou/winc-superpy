import datetime
import superpy.config as config
import superpy.validate as validate


def string_to_number(value:str):
    '''
    Functie voor het omzetten van een string type naar 
    een getal type indien de opgegeven string een getal is.
    '''
    if value.isdigit() or (value.startswith('-') and value.isdigit()):
        return int(value)
    elif value.replace('.','',1).isdigit():
        return float(value)
    return value


def date_str_to_text(date:str):
    '''
    Functie voor het omzetten van datum notatie naar text.
    '''
    if validate.date_format(date):
        date_parts = len(date.split("-"))
        date_format = config.data["date_format"]
        date_format_parts = date_format.split("-")
        date_format = "-".join(date_format_parts[0:date_parts])
        dt = datetime.datetime.strptime(date, date_format)
        if len(date) == 7:
            date_format = "%B %Y"
        elif len(date) == 4:
            date_format = "%Y"
        else:
            date_format = "%A %d %B %Y"
        return dt.strftime(date_format)
    return date


def date_str_to_datetime(date:str):
    '''
    Functie voor het omzetten van datum notatie naar datetime object.
    '''
    if validate.date_format(date):
        date_parts = len(date.split("-"))
        date_format = config.data["date_format"]
        date_format_parts = date_format.split("-")
        date_format = "-".join(date_format_parts[0:date_parts])
        return datetime.datetime.strptime(date, date_format)
    return date