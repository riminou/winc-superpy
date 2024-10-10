import os
import calendar
from datetime import date, datetime

import superpy.config as config
import superpy.validate as validate
import superpy.io as io
import superpy.current_date as current_date
import superpy.convert as convert


CSV_BOUGHT_HEADER = ['id','name','buy_price', 'quantity', 'buy_date','expiration_date']
CSV_SOLD_HEADER = ['id','name','sell_price','quantity', 'sell_date']


def get_product_id():
    '''
    Functie voor het bepalen van de id voor nieuw gekocht product.
    '''
    products = io.read_csv(config.data["files"]["bought"])
    if products:
        products.reverse()
        new_product_id = int(products[0]['id']) + 1
        return new_product_id
    return 1


def buy(product_name: str,
        price: float,
        expiration_date: str,
        quantity: int=1,
        buy_date:str='',
        product_id:int=0):
    '''
    Functie voor het kopen van een product.
        product_name = naam van het product
        price = prijs van het product
        expiration_date = vervaldatum van het product
        quantity = product aantal
    '''
    if buy_date == '':
        buy_date = current_date.get()
    if (validate.price(price)
        and validate.quantity(quantity)
        and validate.expiration_date(buy_date, expiration_date)):
        if product_id < 1:
            product_id = get_product_id()
        new_product = {
            "id": product_id,
            "name": product_name,
            "buy_price": price,
            "quantity": quantity,
            "buy_date": buy_date,
            "expiration_date": expiration_date
        }
        if io.write_csv(new_product, config.data["files"]["bought"]):
            return product_id
    return False


def get_values_to_compare(product:dict,
                          product_property:str,
                          criteria:str,
                          operator:str):
    '''
    Functie voor het bepalen van de correcte waardes om te kunnen vergelijken.
    '''
    if '_date' in product_property:
        criteria_value = convert.date_str_to_datetime(criteria)
        if len(criteria) == 4:
            if operator == '<=' or operator == '>':
                last_day = calendar.monthrange(criteria_value.year, 12)
                criteria_value=datetime(year=criteria_value.year,
                                        month=12,
                                        day=last_day[1])
            elif operator == '>=' or operator == '<':
                criteria_value=datetime(year=criteria_value.year,
                                        month=1,
                                        day=1)
        elif len(criteria) == 7:
            if operator == '<=' or operator == '>':
                last_day = calendar.monthrange(criteria_value.year,
                                               criteria_value.month)
                criteria_value=datetime(year=criteria_value.year,
                                        month=criteria_value.month,
                                        day=last_day[1])
            elif operator == '>=' or operator == '<':
                criteria_value=datetime(year=criteria_value.year,
                                        month=criteria_value.month,
                                        day=1)
        product_value = convert.date_str_to_datetime(product[product_property])
    else:
        criteria_value = convert.string_to_number(criteria)
        product_value = convert.string_to_number(product[product_property])
    return product_value, criteria_value


def filter_products(products:list, filter:str=''):
    '''
    Functie voor het filteren van producten.
        products = een list met producten.
        filters =  een filter voor het zoeken van producten.
            Een filter heeft de syntax '[csv_header_name][operator][value]'
            en ondersteund de operators '==','!=','<=','>=','<<','>>'.
            Voorbeeld: 'product_name==mango'
    '''
    found_products = []
    if filter != '':
        if '==' in filter:
            criteria = filter.split('==')
            if len(criteria) == 2 and criteria[1] != '':
                if '_date' in criteria[0]:
                    found_products = [product for product in products if product[criteria[0]].startswith(criteria[1])]
                else:
                    found_products = [product for product in products if product[criteria[0]] == criteria[1]]
            else:
                found_products = products
        elif '!=' in filter:
            criteria = filter.split('!=')
            if len(criteria) == 2 and criteria[1] != '':
                if '_date' in criteria[0]:
                    found_products = [product for product in products if not product[criteria[0]].startswith(criteria[1])]
                else:
                    found_products = [product for product in products if product[criteria[0]] != criteria[1]]
            else:
                found_products = products
        elif '<=' in filter:
            criteria = filter.split('<=')
            if len(criteria) == 2 and criteria[1] != '':
                for product in products:
                    product_value, criteria_value = get_values_to_compare(product=product,
                                                                          product_property=criteria[0],
                                                                          criteria=criteria[1],
                                                                          operator='<=')
                    if product_value <= criteria_value:
                        found_products.append(product)
            else:
                found_products = products
        elif '>=' in filter:
            criteria = filter.split('>=')
            if len(criteria) == 2 and criteria[1] != '':
                for product in products:
                    product_value, criteria_value = get_values_to_compare(product=product,
                                                                          product_property=criteria[0],
                                                                          criteria=criteria[1],
                                                                          operator='>=')
                    if product_value >= criteria_value:
                        found_products.append(product)
            else:
                found_products = products
        elif '<<' in filter:
            criteria = filter.split('<<')
            if len(criteria) == 2 and criteria[1] != '':
                for product in products:
                    product_value, criteria_value = get_values_to_compare(product=product,
                                                                          product_property=criteria[0],
                                                                          criteria=criteria[1],
                                                                          operator='<<')
                    if product_value < criteria_value:
                        found_products.append(product)
            else:
                found_products = products
        elif '>>' in filter:
            criteria = filter.split('>>')
            if len(criteria) == 2 and criteria[1] != '':
                for product in products:
                    product_value, criteria_value = get_values_to_compare(product=product,
                                                                          product_property=criteria[0],
                                                                          criteria=criteria[1],
                                                                          operator='>>')
                    if product_value > criteria_value:
                        found_products.append(product)
            else:
                found_products = products
        else:
            found_products = products
    else:
        found_products = products
    return found_products


def filter_product_list(products:list, filters:list=[]):
    '''
    Functie voor het ophalen van producten op basis van een filter.
        products = een list met producten.
        filters =  een list met 1 of meerdere filters voor het zoeken van producten.
            Een filter heeft de syntax '[csv_header_name][operator][value]' en
            onderstend de operators '==','!=','<=','>=','<<','>>'.
            Voorbeeld: '[product_name==mango', 'buy_date<=2024-09-03']
    '''
    if len(filters) != 0:
        for filter in filters:
            products = filter_products(products, filter)
    return products


def get_bought_products(product_name:str='',
                        buy_date:str=''):
    '''
    Functie voor het ophalen van gekochte producten.
        product_name = productnaam om op te halen.
            Indien geen productnaam is opgegeven zullen alle 
            producten opgehaald worden.
        buy_date = de datum waaraan het product dient te voldoen.
            Indien geen datum is opgegeven zullen alle data van
            het product opgehaald worden.
    '''
    found_products = []
    product_quantity = 0
    products = io.read_csv(config.data["files"]["bought"])
    if products:
        product_filters = [f'name=={product_name}',f'buy_date=={buy_date}']
        found_products = filter_product_list(products, product_filters)
        product_quantity = sum([int(product['quantity']) for product in found_products])
    return found_products, product_quantity


def get_sold_products(product_name:str="",
                      sell_date:str=""):
    '''
    Functie voor het bepalen welke en hoeveel producten verkocht zijn.
        product_name = de productnaam, indien geen naam wordt opgegeven
            dan worden alle verkochte producten opgehaald.
    '''
    found_products = []
    product_quantity = 0
    products = io.read_csv(config.data["files"]['sold'])
    if products:
        product_filters = [f'name=={product_name}',f'sell_date=={sell_date}']
        found_products = filter_product_list(products, product_filters)
        product_quantity = sum([int(product['quantity']) for product in found_products])
    return found_products, product_quantity


def get_available_products(product_name:str='',
                           product_date:str=''):
    '''
    Functie voor het ophalen van alle beschikbare producten op voorraad.
        product_name = de productnaam, indien geen naam wordt opgegeven
            dan worden alle beschikbare producten opgehaald.
        product_date = de datum waarvoor de beschikbaarheid van een product
            opgevraagd dient te worden, indien geen datum is opgegeven
            zullen producten opgehaald worden met alle aankoopdata.
    '''
    inventory_products = []
    remaining_quantity = 0
    bought_products, bought_quantity = get_bought_products(product_name=product_name)
    bought_filter = [f'buy_date<={product_date}',f'expiration_date>={product_date}']
    available_bought_products = filter_product_list(products=bought_products, filters=bought_filter)
    available_bought_quantity = sum([int(product['quantity']) for product in available_bought_products])
    sold_products, sold_quantity = get_sold_products(product_name=product_name)
    remaining_quantity = available_bought_quantity - sold_quantity
    if remaining_quantity > 0:
        bought_dict = {product['id']:product for product in available_bought_products}
        for sold_product in sold_products:
            sold_product_id = sold_product['id']
            if sold_product_id in bought_dict.keys():
                sold_quantity = int(sold_product['quantity'])
                bought_quantity = int(bought_dict[sold_product_id]['quantity'])
                inventory_quantity = bought_quantity - sold_quantity
                if inventory_quantity < 1:
                    bought_dict.pop(sold_product_id)
                else:
                    bought_dict[sold_product_id]['quantity'] = str(inventory_quantity)
        inventory_products = list(bought_dict.values())
        remaining_quantity = sum(int(product['quantity']) for product in inventory_products)
    if len(inventory_products) == 0:
        # Indien geen producten zijn gevonden
        # dan een leeg product toevoegen.
        empty_product = {}
        for element in CSV_BOUGHT_HEADER:
            empty_product[element] = '0'
        inventory_products.append(empty_product)
    return inventory_products, remaining_quantity


def get_expired_products(product_name:str='',
                         product_date:str=''):
    '''
    Functie voor het ophalen van producten die verlopen zijn.
    '''
    remaining_expired_products = []
    bought_products, quantity = get_bought_products(product_name=product_name)
    filter = [f'expiration_date=={product_date}', f'expiration_date<={product_date}']
    expired_products = filter_product_list(bought_products, filter)
    sold_products, sold_quantity = get_sold_products(product_name=product_name)
    sold_filter = [f'sell_date<={product_date}']
    sold_products = filter_product_list(sold_products, sold_filter)
    if sold_quantity > 0:
        for product in expired_products:
            product_id = product['id']
            id_filter = [f'id=={product_id}']
            sold_expired = filter_product_list(sold_products, id_filter)
            if len(sold_expired) > 0:
                sold_expired_quantity = sum([int(product['quantity']) for product in sold_expired])
                expired_quantity = int(product['quantity']) - sold_expired_quantity
                if expired_quantity > 0:
                    product['quantity'] = str(expired_quantity)
                    remaining_expired_products.append(product)
    else:
        remaining_expired_products = expired_products
    if len(remaining_expired_products) == 0:
        # Indien geen producten zijn gevonden
        # dan een leeg product toevoegen.
        empty_product = {}
        for element in CSV_BOUGHT_HEADER:
            empty_product[element] = '0'
        remaining_expired_products.append(empty_product)
    return remaining_expired_products


def create_product_to_sell(available_product:dict,
                           sell_price:float,
                           sell_quantity:int,
                           sell_date:str):
    '''
    Functie voor het omzetten van een product op voorraad naar een product voor verkoop.
    Hierbij wordt rekening gehouden met het aantal dat al verkocht is van het product.
        available_product = een beschikbaar product geschikt voor verkoop.
        sell_price = de prijs waarvoor het product verkocht gaat worden.
        sell_quantity = het aantal wat verkocht dient te worden.
        sell_date = de verkoopdatum.
    '''
    available_quantity = int(available_product["quantity"])
    remaining_quantity = available_quantity - sell_quantity
    if remaining_quantity >= 0:
        product_to_sell = dict(zip(CSV_SOLD_HEADER,
                                   [available_product["id"],
                                    available_product["name"],
                                    sell_price,
                                    sell_quantity,
                                    sell_date]))
    else:
        product_to_sell = dict(zip(CSV_SOLD_HEADER, [available_product["id"],
                                                     available_product["name"],
                                                     sell_price,
                                                     available_quantity,
                                                     sell_date]))
    return product_to_sell


def create_products_to_sell(available_products:list,
                            sell_price:float,
                            sell_quantity:int,
                            sell_date:str):
    '''
    Functie voor het ophalen van de beschikbare producten voor verkoop.
        available_products = een list met beschikbare producten voor verkoop.
        sold_products = een list met verkochte producten met dezelfde productnaam
        sell_price = de prijs waarvoor het gekochte product verkocht dient te worden
        sell_quantity = het aantal wat verkocht dient te worden
        sell_date = de verkoopdatum
    '''
    products_to_sell = []
    available_products = sorted(available_products, key=lambda d: d['expiration_date'])
    for product in available_products:
        product_to_sell = create_product_to_sell(available_product=product,
                                                 sell_price=sell_price,
                                                 sell_quantity=sell_quantity,
                                                 sell_date=sell_date)
        products_to_sell.append(product_to_sell)
        sell_quantity -= int(product_to_sell['quantity']) 
        if sell_quantity == 0:
            break
    return products_to_sell


def sell(product_name:str,
         price:float,
         quantity:int=1):
    '''
    Functie voor het verkopen van een product.
        product_name = de productnaam
        price = de verkoopprijs
        quantity = het verkoopaantal
    '''
    if validate.price(price=price) and validate.quantity(quantity=quantity):
        sell_date = current_date.get()
        available_products, remaining_quantity = get_available_products(product_name=product_name,
                                                                        product_date=sell_date)
        if remaining_quantity >= quantity:
            products_to_sell = create_products_to_sell(available_products=available_products,
                                                    sell_price=price,
                                                    sell_quantity=quantity,
                                                    sell_date=sell_date)
            for product in products_to_sell:
                io.write_csv(product, config.data["files"]["sold"])
            return True
        else:
            print(f"Oeps... there doesn't seem to be enough '{product_name}' available to sell.")
            print(f"Only {remaining_quantity} remaining...")
    return False


def get_product_revenue(product_name:str="",
                        sell_date:str=""):
    '''
    Functie voor het bepalen van de totale omzet van een product.
        product_name = de productnaam, indien geen naam is opgegeven 
            zal de omzet van alle producten worden bepaald op 
            de opgegeven verkoopdatum.
        sell_date = de verkoopdatum, indien geen verkoopdatum is 
            opgegeven zullen alle producten van alle verkoopdata worden bepaald.
    '''
    sold_products, sold_quantity = get_sold_products(sell_date=sell_date,
                                                     product_name=product_name)
    revenue = 0.0
    revenue += sum(int(product['quantity']) * float(product['sell_price']) for product in sold_products)
    return round(revenue, 2)


def get_product_cost(product_name:str="",
                     buy_date:str=""):
    '''
    Functie voor het bepalen van de totale kosten van een product.
        product_name = de productnaam, indien geen naam is opgegeven 
            zal de kosten van alle producten worden bepaald op 
            de opgegeven aankoopdatum.
        buy_date = de aankoopdatum, indien geen aankoopdatum is 
            opgegeven zullen alle producten van alle aankoopdata worden bepaald.
    '''
    bought_products, bought_quantity = get_bought_products(product_name=product_name,
                                                           buy_date=buy_date)
    purchase_price = 0.0
    purchase_price += sum(int(product['quantity']) * float(product['buy_price']) for product in bought_products)
    return round(purchase_price, 2)


def get_product_profit(product_name:str="",
                       profit_date:str=""):
    '''
    Functie voor het bepalen van de gemaakte winst.
        product_name = de productnaam waarvan de winst berekend
            dient te worden. Indien geen naam is opgegeven worden 
            van alle producten de winst berekend.
        profit_date = de datum waarvoor de winst berekend dient
            te worden. Indien geen datum is opgegeven zal de winst
            van alle data worden berekend.
    '''
    revenue = get_product_revenue(product_name=product_name,
                                  sell_date=profit_date)
    cost = get_product_cost(product_name=product_name,
                            buy_date=profit_date)
    profit = revenue - cost
    return round(profit, 2)
    

def import_products_from_file(file:str):
    '''
    Functie voor het importeren van producten d.m.v. een bestand.
        file = het bestand met producten om te importeren.
    '''
    products = []
    full_filename = os.path.abspath(file)
    extension = os.path.splitext(full_filename)[1]
    print(f'Importing products from "{full_filename}"...')
    if extension == '.csv':
        products = io.read_csv(full_filename)
    elif extension == '.json':
        products = io.read_json(full_filename)
    elif extension == '.xml':
        products = io.read_xml(full_filename)
    else:
        print(f'ERROR: Filetype "{extension}" not supported for import.')
        return False
    if len(products) > 0:
        product_id = get_product_id()
        for product in products:
            buy(product_name=product['name'],
                price=float(product['buy_price']),
                quantity=int(product['quantity']),
                expiration_date=product['expiration_date'],
                buy_date=product['buy_date'],
                product_id=product_id)
            product_id += 1
        print(f'Succesfully imported "{len(products)}" products.')
    else:
        print('No products found to import...')
    return True


def export_products_to_file(file:str, products:list=[]):
    '''
    Functie voor het exporteren van producten naar een bestand.
        file = het bestand met producten om naar te exporteren.
    '''
    if len(products) == 0:
        products, quantity = get_bought_products()
    if len(products) > 0:
        full_filename = os.path.abspath(file)
        extension = os.path.splitext(full_filename)[1]
        print(f'Exporting products to "{full_filename}"...')
        if extension == '.csv':
            for product in products:
                if not io.write_csv(content=product,
                                    csv_file=full_filename):
                    return False
            return True
        elif extension == '.json':
            return io.write_json(product_list=products,
                                 json_file=full_filename)
        elif extension == '.xml':
            return io.write_xml(product_list=products,
                                xml_file=full_filename)
        else:
            print(f'ERROR: Filetype "{extension}" not supported for export.')
    return False
