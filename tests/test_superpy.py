import pytest
import json
import random
import csv

from math import fsum
from datetime import datetime
from datetime import timedelta

import superpy.io as io
import superpy.config as config
import superpy.current_date as current_date
import superpy.inventory as inventory
import superpy.validate as validate
import superpy.report as report
import superpy.convert as convert


@pytest.fixture
def superpy_test_folder(tmp_path):
    return tmp_path


@pytest.fixture
def example_config_data(superpy_test_folder):
    return {
        "version": "test.version",
        "description": "Test configuratie bestand voor het test van de superpy applicatie.",
        "files": {
            "sold": f"{superpy_test_folder}\\test_sold.csv",
            "bought": f"{superpy_test_folder}\\test_bought.csv",
            "current_date": f"{superpy_test_folder}\\test_current_date.csv"
        },
        "date_format": "%Y-%m-%d",
        "test": {
            "product_range" : 100,
            "current_date" : "2024-02-04",
            "max_past_days" : 6,
            "max_future_days" : 14,
            "folder": f"{superpy_test_folder}"
        }
    }


@pytest.fixture
def example_config(superpy_test_folder, example_config_data):
    config_file = superpy_test_folder / "test_config.json"
    with open(config_file, "w") as outfile: 
        json.dump(example_config_data, outfile)
    if (config.init_config(config_file)):
        return config.data
    return None


@pytest.fixture
def example_dates(example_config):
    product_range = example_config["test"]["product_range"]
    current_date = datetime.now()
    min_past_date = current_date - timedelta(days=6)
    max_future_date = current_date + timedelta(days=14)
    example_dates = [min_past_date]
    while min_past_date != max_future_date:
        min_past_date += timedelta(days=1)
        example_dates.append(min_past_date)
    return random.choices(example_dates, k=product_range)


@pytest.fixture
def example_products(example_config):
    product_range = example_config["test"]["product_range"]
    products = [
        "orange",
        "apple",
        "mango",
        "avocado",
        "strawberry",
        "pineapple",
        "guava",
        "pear",
        "watermelon",
        "lime"
    ]
    return random.choices(products, k=product_range)


@pytest.fixture
def example_bought_products(example_config, example_dates, example_products):
    product_range = example_config["test"]["product_range"]
    example_bought_products = []
    for n in range(1, product_range):
        random_price = round(random.uniform(0.0, 10.0), 2)
        random_quantity = random.randint(1, 100)
        example_date = example_dates[n]
        example_buy_date = example_date.strftime(example_config["date_format"])
        example_expiration_date = (example_date + timedelta(days=7)).strftime(example_config["date_format"])
        example_bought_products.append({
            "id": str(n),
            "name": example_products[n],
            "buy_price" : str(random_price),
            "quantity" : str(random_quantity),
            "buy_date" : example_buy_date,
            "expiration_date" : example_expiration_date
        })
    return example_bought_products


@pytest.fixture
def example_sold_products(example_config, example_bought_products):
    product_range = int(example_config["test"]["product_range"])
    products_to_sell = random.choices(example_bought_products, k=int(product_range * 0.5))
    example_sold_products = []
    for product in products_to_sell:
        product_list =  [item for item in products_to_sell if item['name'] == product["name"]]
        sold_product = {}
        sold_product["id"] = product["id"]
        sold_product["name"] = product["name"]
        sold_product["sell_price"] = str(round((float(product["buy_price"]) * 2.5), 2))
        sold_product["quantity"] = str(random.randint(1, 10))
        future_day = random.randint(1,7)
        sell_date = datetime.strptime(product["buy_date"], example_config["date_format"]) + timedelta(days=future_day)
        sold_product["sell_date"] = sell_date.strftime(example_config["date_format"])
        example_sold_products.append(sold_product)
    return example_sold_products


@pytest.fixture
def example_bought_csv_file(example_config_data, example_bought_products):
    csv_file = example_config_data["files"]["bought"]
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(list(example_bought_products[0].keys()))
        writer.writerows([product.values() for product in example_bought_products])
    return csv_file


@pytest.fixture
def example_sold_csv_file(example_config_data, example_sold_products):
    csv_file = example_config_data["files"]["sold"]
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(list(example_sold_products[0].keys()))
        writer.writerows([product.values() for product in example_sold_products])
    return csv_file


def test_io_write_csv(example_config, example_bought_products):
    csv_file = example_config["files"]["bought"]    
    for data_row in example_bought_products:
        io.write_csv(data_row, csv_file)
    example_csv_data = []
    example_csv_header = ";".join(list(example_bought_products[0].keys()))
    example_csv_data = [";".join(row.values()) for row in example_bought_products]
    csv_data = []
    with open(csv_file, "r") as f:
        for readline in f:
            csv_data.append(readline.strip())
    csv_header_to_test = csv_data[0]
    assert csv_header_to_test == example_csv_header
    assert csv_data[1:] == example_csv_data


def test_io_read_csv(example_bought_products, example_bought_csv_file):
    csv_data = io.read_csv(example_bought_csv_file)
    assert csv_data == example_bought_products


def test_io_write_json(example_config, example_bought_products):
    json_file = f'{example_config["test"]["folder"]}\\test_export.json'
    write_result = io.write_json(product_list=example_bought_products, json_file=json_file)
    with open(json_file, 'r') as jsonfile:
        json_data = json.load(jsonfile)
    assert write_result
    assert example_bought_products == json_data


def test_io_read_json(example_config, example_bought_products):
    json_file = f'{example_config["test"]["folder"]}\\test_import.json'
    with open(json_file, 'w') as jsonfile:
        json.dump(example_bought_products, jsonfile)
    read_result = io.read_json(json_file=json_file)
    assert example_bought_products == read_result


def test_io_write_xml(example_config, example_bought_products):
    xml_file = f'{example_config["test"]["folder"]}\\test_export.xml'
    write_result = io.write_xml(product_list=example_bought_products, xml_file=xml_file)
    xml_data = []
    with open(xml_file, 'r') as xmlfile:
        delimiters = ["<", ">"]
        for line in xmlfile.readlines():
            if line.strip() == '<product>':
                product = {}
            elif line.strip() == '</product>':
                xml_data.append(product)
            else:
                indexes = [index for index in range(len(line)) if line[index] in delimiters]
                if len(indexes) == 4:
                    key = line[indexes[0]+1:indexes[1]]
                    value = line[indexes[1]+1:indexes[2]]
                    product[key] = value
    assert write_result
    assert xml_data == example_bought_products


def test_io_read_xml(example_config, example_bought_products):
    xml_file = f'{example_config["test"]["folder"]}\\test_import.xml'
    io.write_xml(product_list=example_bought_products, xml_file=xml_file)
    read_result = io.read_xml(xml_file=xml_file)
    assert read_result == example_bought_products
    

def test_validate_date_format(example_config):
    date_format = example_config["date_format"]
    example_date = datetime.now().strftime(example_config["date_format"])
    example_date_parts = example_date.split('-')
    
    ''' Test with year-month-day in date '''
    assert validate.date_format(example_date)
    
    ''' Test with year-month in date '''
    example_date = f'{example_date_parts[0]}-{example_date_parts[1]}'
    assert validate.date_format(example_date)
    
    ''' Test with only year in date '''
    example_date = f'{example_date_parts[0]}'
    assert validate.date_format(example_date)
    
    ''' Test with wrong date sequence '''
    example_date = f'{example_date_parts[1]}-{example_date_parts[0]}'
    assert validate.date_format(example_date) == False


def test_current_date_get(example_config):
    example_current_date = datetime.now().strftime(example_config["date_format"])
    current_date_to_test = current_date.get()
    assert current_date_to_test == example_current_date


def test_current_date_set(example_config, superpy_test_folder):
    ''' Test with a current_date file that doesn't exist. '''
    current_date_file = example_config["files"]["current_date"]
    example_new_date = datetime.now().strftime(example_config["date_format"])
    current_date.set(example_new_date)
    with open(current_date_file, "r") as csv_file:
        last_line = csv_file.readlines()[-1]
        new_date_to_test = last_line.strip()
    assert new_date_to_test == example_new_date
    
    ''' Test with a current_date file that allready exist. '''
    new_date = datetime.now() + timedelta(days=1)
    example_new_date = new_date.strftime(example_config["date_format"])
    current_date.set(example_new_date)
    with open(current_date_file, "r") as csv_file:
        last_line = csv_file.readlines()[-1]
        new_date_to_test = last_line.strip()
    assert new_date_to_test == example_new_date
    

def test_current_date_advance(example_config):
    ''' Test with a positive number. '''
    advance_days = 2
    example_current_date = datetime.now() + timedelta(days=advance_days)
    formatted_current_date = example_current_date.strftime(example_config["date_format"])
    advanced_date = current_date.advance(advance_days)
    assert advanced_date == formatted_current_date
    
    ''' Test with a negative number. '''
    example_date = datetime.now().strftime(example_config["date_format"])
    reduce_days = -2
    reduced_date = current_date.advance(reduce_days)
    assert reduced_date == example_date


def test_current_date_reset(example_config, superpy_test_folder):
    current_date_file = superpy_test_folder / "test_current_date.csv"
    past_date = "2023-08-25"
    csv_header = "current_date"
    current_date_file.write_text('{}\n{}'.format(csv_header, past_date))
    current_date.reset()
    current_date_now = datetime.now().strftime(example_config["date_format"])
    new_date_to_test = current_date_file.read_text().split('\n')[1]
    assert current_date_now == new_date_to_test 


def test_convert_string_to_number():
    ''' Test convert to string '''
    assert convert.string_to_number('test') == 'test'
    ''' Test convert to int '''
    assert convert.string_to_number('1') == 1
    ''' Test convert to float '''
    assert convert.string_to_number('1.23') == 1.23
    

def test_convert_date_str_to_text(example_config):
    ''' Test full date. '''
    example_date = "2024-08-25"
    example_date_text = "Sunday 25 August 2024"
    month = example_date[0:7:]
    year = example_date[0:4:]
    date_text = convert.date_str_to_text(example_date)
    assert date_text == example_date_text
    
    ''' Test with year and month. '''
    example_date = "2024-08"
    example_date_text = "August 2024"
    date_text = convert.date_str_to_text(example_date)
    assert date_text == example_date_text


def test_inventory_filter_products(example_config,
                                   example_bought_products):
    ''' Test with no filter. '''
    available_products = inventory.filter_products(example_bought_products, '')
    assert available_products == example_bought_products
    ''' Test '==' operator in filter. '''
    example_product = example_bought_products[0]
    product_name = example_product["name"]
    example_products = [
        product for product in example_bought_products if product['name'] == product_name
    ]
    available_products = inventory.filter_products(products=example_bought_products,
                                                   filter=f'name=={product_name}')
    assert available_products == example_products
    ''' Test '!=' operator in filter '''
    example_products = [
        product for product in example_bought_products if product['name'] != product_name
    ]
    available_products = inventory.filter_products(products=example_bought_products,
                                                   filter=f'name!={product_name}')
    assert available_products == example_products
    ''' Test '<=' operator in filter. '''
    product_buy_date = example_product["buy_date"]
    example_products = [
        product for product in example_bought_products if product['buy_date'] <= product_buy_date
    ]
    available_products = inventory.filter_products(products=example_bought_products,
                                                   filter=f'buy_date<={product_buy_date}')
    assert available_products == example_products
    ''' Test '<<' operator in filter. '''
    product_buy_price = float(example_product["buy_price"])
    example_products = [
        product for product in example_bought_products if float(product['buy_price']) < product_buy_price
    ]
    available_products = inventory.filter_products(products=example_bought_products,
                                                   filter=f'buy_price<<{product_buy_price}')
    assert available_products == example_products
    ''' Test '>>' operator in filter. '''
    product_quantity = int(example_product["quantity"])
    example_products = [
        product for product in example_bought_products if int(product['quantity']) > product_quantity
    ]
    available_products = inventory.filter_products(products=example_bought_products,
                                                   filter=f'quantity>>{product_quantity}')
    assert available_products == example_products


def test_inventory_filter_product_list(example_config,
                                       example_bought_products):
    available_products = inventory.filter_product_list(products=example_bought_products)
    ''' Test with no filters. '''
    assert available_products == example_bought_products
    ''' Test with one filter. '''
    example_product = example_bought_products[0]
    product_name = example_product["name"]
    example_products = [
        product for product in example_bought_products if product['name'] == product_name
    ]
    available_products = inventory.filter_product_list(products=example_bought_products,
                                                filters=[f'name=={product_name}'])
    assert available_products == example_products
    ''' Test with multiple filters. '''
    product_buy_date = example_product["buy_date"]
    example_products = [
        product for product in example_bought_products if product['name'] == product_name 
        and product['buy_date'] == product_buy_date
        ]
    filters = [f'name=={product_name}',
               f'buy_date=={product_buy_date}']
    available_products = inventory.filter_product_list(products=example_bought_products,
                                                filters=filters)
    assert available_products == example_products
    example_products = [
        product for product in example_bought_products if product['name'] == product_name 
        and product['buy_date'] <= product_buy_date
        and product['expiration_date'] >= product_buy_date
        ]
    filters = [f'name=={product_name}',
               f'buy_date<={product_buy_date}',
               f'expiration_date>={product_buy_date}']
    available_products = inventory.filter_product_list(products=example_bought_products,
                                                filters=filters)
    assert available_products == example_products


def test_inventory_get_bought_products(example_config, 
                                       example_bought_csv_file,
                                       example_bought_products):
    ''' Test with no product_name and current_date. '''
    available_products, product_quantity = inventory.get_bought_products()
    example_product_quantity = sum([
        int(product['quantity']) for product in example_bought_products
    ])
    assert available_products != None 
    assert available_products == example_bought_products
    assert product_quantity == example_product_quantity
    
    ''' Test with no current_date. '''
    example_product = example_bought_products[0]
    product_name = example_product["name"]
    available_products, product_quantity = inventory.get_bought_products(product_name=product_name)
    example_products = [
        product for product in example_bought_products if product['name'] == product_name
    ]
    example_product_quantity = sum([
        int(product['quantity']) for product in example_products
    ])
    assert available_products != None
    assert available_products == example_products
    assert product_quantity == example_product_quantity
    
    ''' Test with no product_name. '''
    example_product = example_bought_products[0]
    product_name = ''
    example_date = example_product["buy_date"]
    available_products, product_quantity = inventory.get_bought_products(buy_date=example_date)
    example_products = [
        product for product in example_bought_products if product['buy_date'] == example_date
    ]
    example_product_quantity = sum([
        int(product['quantity']) for product in example_products
    ])
    assert available_products != None
    assert available_products == example_products[0:]
    assert product_quantity == example_product_quantity
    
    ''' Test with one specific product. '''
    example_product = example_bought_products[0]
    product_name = example_product["name"]
    example_date = example_product["buy_date"]
    available_products, product_quantity = inventory.get_bought_products(product_name=product_name, 
                                                                         buy_date=example_date)
    example_products = [
        product for product in example_bought_products if product['name'] == product_name 
        and product['buy_date'] == example_date
    ]
    example_product_quantity = sum([
        int(product['quantity']) for product in example_products
    ])
    assert available_products != None
    assert available_products == example_products[0:]
    assert product_quantity == example_product_quantity


def test_inventory_get_sold_products(example_config,
                                     example_sold_csv_file,
                                     example_sold_products):
    ''' Test with no product_name and sell_date. '''
    available_products, product_quantity = inventory.get_sold_products()
    example_product_quantity = sum([
        int(product['quantity']) for product in example_sold_products
    ])
    assert available_products == example_sold_products
    assert product_quantity == example_product_quantity
    
    ''' Test with a product name'''
    example_product = example_sold_products[0]
    product_name = example_product["name"]
    available_products, product_quantity = inventory.get_sold_products(product_name=product_name)    
    example_products = [
        product for product in example_sold_products if product['name'] == product_name
    ]
    example_product_quantity = sum([
        int(product['quantity']) for product in example_products
    ])   
    assert available_products == example_products
    assert product_quantity == example_product_quantity
    
    ''' Test with product sell date. '''
    example_sell_date = example_product["sell_date"]
    available_products, product_quantity = inventory.get_sold_products(sell_date=example_sell_date)
    example_products = [
        product for product in example_sold_products if product['sell_date'] == example_sell_date
    ]
    example_product_quantity = sum([
        int(product['quantity']) for product in example_products
    ])
    assert available_products == example_products
    assert product_quantity == example_product_quantity
    
    
    ''' Test with product name and sell date. '''
    available_products, product_quantity = inventory.get_sold_products(product_name=product_name,
                                                                       sell_date=example_sell_date)
    example_products = [
        product for product in example_sold_products if product['name'] == product_name
        and product['sell_date'] == example_sell_date
    ]
    example_product_quantity = sum([
        int(product['quantity']) for product in example_products
    ])
    assert available_products == example_products
    assert product_quantity == example_product_quantity


def test_inventory_buy(example_config,
                       example_bought_products):
    ''' Test with correct arguments. '''
    for product in example_bought_products:
        inventory.buy(
            product_name=product["name"],
            price=float(product["buy_price"]),
            quantity=int(product["quantity"]),
            expiration_date=product["expiration_date"],
            buy_date=product["buy_date"]
        )
    csv_file = example_config['files']['bought']
    example_csv_data = []
    example_csv_header = ";".join(list(example_bought_products[0].keys()))
    example_csv_data = [";".join(row.values()) for row in example_bought_products]
    csv_data = []
    with open(csv_file, "r") as f:
        for readline in f:
            csv_data.append(readline.strip())
    csv_header_to_test = csv_data[0]
    assert csv_header_to_test == example_csv_header
    assert csv_data[1:] == example_csv_data
    
    ''' Test with invalid price. '''
    price = -1.8
    quantity = 1
    expiration_date = (datetime.now() + timedelta(days=7)).strftime(example_config["date_format"])
    buy_result = inventory.buy(product_name="water", 
                           price=price, 
                           expiration_date=expiration_date,
                           quantity= quantity)
    assert buy_result == False
    
    ''' Test with invalid quantity. '''
    price = 0.8
    quantity = 0
    buy_result = inventory.buy(product_name="water", 
                           price=price, 
                           expiration_date=expiration_date,
                           quantity= quantity)
    assert buy_result == False
    
    ''' Test with invalid expiration_date. '''
    price = 0.8
    expiration_date = "2018-01-01"
    buy_result = inventory.buy(product_name="water", 
                           price=price, 
                           expiration_date=expiration_date,
                           quantity= quantity)
    assert buy_result == False


def test_inventory_create_product_to_sell(example_config,
                                          example_bought_products):
    ''' Test with enough available products. '''
    available_product = example_bought_products[0]
    sell_price = float(available_product['buy_price']) * 2
    sell_quantity = int(available_product['quantity']) - 1
    sell_date = datetime.now().strftime(example_config["date_format"])
    product_to_sell = inventory.create_product_to_sell(available_product=available_product,
                                                       sell_price=sell_price,
                                                       sell_quantity=sell_quantity,
                                                       sell_date=sell_date)
    sold_product = {}
    sold_product["id"] = available_product["id"]
    sold_product["name"] = available_product["name"]
    sold_product["sell_price"] = sell_price
    sold_product["quantity"] = sell_quantity
    sold_product['sell_date'] = sell_date
    assert product_to_sell == sold_product
    
    ''' Test with not enough available products. '''
    sell_quantity = int(available_product['quantity']) + 1
    product_to_sell = inventory.create_product_to_sell(available_product=available_product,
                                                       sell_price=sell_price,
                                                       sell_quantity=sell_quantity,
                                                       sell_date=sell_date)
    sold_product["quantity"] = int(available_product['quantity'])
    assert product_to_sell == sold_product


def test_inventory_create_products_to_sell(example_config,
                                           example_bought_products):
    ''' Test with enough products. '''
    available_product_1 = example_bought_products[0].copy()
    available_product_2 = example_bought_products[0].copy()
    available_product_2['id'] = str(int(available_product_1['id']) + 1)
    available_products = [available_product_1, available_product_2]
    sell_price = float(available_product_1['buy_price']) * 2
    sell_quantity = (int(available_product_1['quantity']) * 2) - 1
    sell_date = datetime.now().strftime(example_config["date_format"])
    products_to_sell = inventory.create_products_to_sell(available_products=available_products,
                                                         sell_price=sell_price,
                                                         sell_quantity=sell_quantity,
                                                         sell_date=sell_date)
    sold_product_1 = {}
    sold_product_1["id"] = available_product_1["id"]
    sold_product_1["name"] = available_product_1["name"]
    sold_product_1["sell_price"] = sell_price
    sold_product_1["quantity"] = int(available_product_1["quantity"])
    sold_product_1['sell_date'] = sell_date
    sold_product_2 = sold_product_1.copy()
    sold_product_2["id"] = available_product_2["id"]
    sold_product_2["quantity"] = int(available_product_1["quantity"]) - 1
    sold_products = [sold_product_1, sold_product_2]
    assert products_to_sell == sold_products
    
    ''' Test with not enough products. '''
    sell_quantity = (int(available_product_1['quantity']) * 2) + 1
    products_to_sell = inventory.create_products_to_sell(available_products=available_products,
                                                         sell_price=sell_price,
                                                         sell_quantity=sell_quantity,
                                                         sell_date=sell_date)
    sold_product_2["quantity"] = int(available_product_1["quantity"])
    sold_products = [sold_product_1, sold_product_2]
    assert products_to_sell == sold_products


def test_inventory_sell(example_config,
                        example_bought_csv_file,
                        example_bought_products,
                        example_sold_csv_file,
                        example_sold_products):
    current_date = datetime.now().strftime(example_config["date_format"])
    expiration_date = (datetime.now() + timedelta(days=7)).strftime(example_config["date_format"])
    example_product = example_bought_products[0]
    product_name = example_product["name"]
    bought_products = [
        product for product in example_bought_products if product['name'] == product_name 
        and product['buy_date'] <= current_date < product['expiration_date']
    ]
    bought_quantity = sum([
        int(product['quantity']) for product in bought_products
    ])
    sold_products = [
        product for product in example_sold_products if product['name'] == product_name 
    ]
    sold_quantity = sum([
        int(product['quantity']) for product in sold_products
    ])
    
    ''' Test with the product not available. '''
    sell_price = round(float(example_product["buy_price"]) * 2.5, 2)
    sell_quantity = bought_quantity + 1
    sell_result = inventory.sell(product_name=product_name,
                             price=sell_price,
                             quantity=sell_quantity)
    assert sell_result == False

    ''' Test with a product available. '''
    product_id = int(example_config["test"]["product_range"])
    new_quantity = 0
    if bought_quantity <= sold_quantity:
        new_quantity = (sold_quantity - bought_quantity) + 1
        new_product = [product_id,
                       example_product["name"],
                       example_product["buy_price"],
                       new_quantity,
                       current_date,
                       expiration_date
        ]
        with open(example_bought_csv_file, "a", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(new_product)
    else:
        new_quantity = bought_quantity - sold_quantity
    sell_result = inventory.sell(product_name=product_name,
                                 price=sell_price,
                                 quantity=new_quantity)
    with open(example_sold_csv_file, 'r') as f:
        last_line = f.readlines()[-1]
        sold_product = last_line.strip().split(';')
    assert sell_result == True
    assert sold_product[1] == product_name 
    assert sold_product[2] == str(sell_price)
    assert sold_product[4] == current_date

    ''' Test with product allready sold. '''
    sell_result = inventory.sell(product_name=product_name,
                             price=sell_price,
                             quantity=new_quantity)
    assert sell_result == False


def test_inventory_import(example_config,
                          example_bought_products):
    ''' Test voor import producten uit csv. '''
    bought_products_csv = example_config['files']['bought']
    total_product_quantity = len(example_bought_products)
    last_product_id = example_bought_products[-1]['id']
    csv_file = f'{example_config["test"]["folder"]}\\test_import.csv'
    for product in example_bought_products:
        io.write_csv(content=product, csv_file=csv_file)    
    assert inventory.import_products_from_file(file=csv_file)
    new_products = io.read_csv(csv_file=bought_products_csv)
    new_product_quantity = len(new_products)
    new_last_product_id = new_products[-1]['id']
    assert new_product_quantity == total_product_quantity
    assert new_last_product_id == last_product_id
    
    ''' Test voor import producten uit json. '''
    last_product_id = str(int(new_last_product_id) + len(example_bought_products))
    total_product_quantity += len(example_bought_products)
    json_file = f'{example_config["test"]["folder"]}\\test_import.json'
    io.write_json(product_list=example_bought_products, json_file=json_file)
    assert inventory.import_products_from_file(file=json_file)
    new_products = io.read_csv(csv_file=bought_products_csv)
    new_product_quantity = len(new_products)
    new_last_product_id = new_products[-1]['id']
    assert new_product_quantity == total_product_quantity
    assert new_last_product_id == last_product_id

    ''' Test voor import producten uit xml. '''
    last_product_id = str(int(new_last_product_id) + len(example_bought_products))
    total_product_quantity += len(example_bought_products)
    xml_file = f'{example_config["test"]["folder"]}\\test_import.xml'
    io.write_xml(product_list=example_bought_products, xml_file=xml_file)    
    assert inventory.import_products_from_file(file=xml_file)
    new_products = io.read_csv(csv_file=bought_products_csv)
    new_product_quantity = len(new_products)
    new_last_product_id = new_products[-1]['id']
    assert new_product_quantity == total_product_quantity
    assert new_last_product_id == last_product_id


def test_inventory_export(example_config,
                          example_bought_csv_file,
                          example_bought_products):
    ''' Test export van producten naar csv. '''
    export_file = f'{example_config["test"]["folder"]}\\test_export.csv'
    inventory.export_products_to_file(file=export_file)
    exported_products = io.read_csv(csv_file=export_file)
    assert exported_products == example_bought_products
    
    ''' Test export van producten naar json. '''
    export_file = f'{example_config["test"]["folder"]}\\test_export.json'
    inventory.export_products_to_file(file=export_file)
    exported_products = io.read_json(json_file=export_file)
    assert exported_products == example_bought_products
    
    ''' Test export van producten naar xml. '''
    export_file = f'{example_config["test"]["folder"]}\\test_export.xml'
    inventory.export_products_to_file(file=export_file)
    exported_products = io.read_xml(xml_file=export_file)
    assert exported_products == example_bought_products


def test_inventory_get_product_revenue(example_config,
                                       example_sold_csv_file,
                                       example_sold_products):
    ''' Test revenue of all products '''
    example_revenue = 0.0
    for product in example_sold_products:
        example_revenue += float(product['sell_price']) * int(product['quantity'])
    revenue = inventory.get_product_revenue()
    assert revenue == round(example_revenue, 2)
    
    ''' Test revenue with a product name '''
    example_product = example_sold_products[0]
    product_name = example_product["name"]
    example_revenue = 0.0
    for product in example_sold_products:
        if product['name'] == product_name:
            example_revenue += float(product['sell_price']) * int(product['quantity'])
    revenue = inventory.get_product_revenue(product_name=product_name)
    assert revenue == round(example_revenue, 2)
    
    ''' Test revenue on a specific date '''
    sell_date = example_product["sell_date"]
    example_revenue = 0.0
    for product in example_sold_products:
        if product['sell_date'] == sell_date:
            example_revenue += float(product['sell_price']) * int(product['quantity'])
    revenue = inventory.get_product_revenue(sell_date=sell_date)
    assert revenue == round(example_revenue, 2)
    
    ''' Test revenue within a month'''
    sell_date_month = sell_date[0:7:]
    example_revenue = 0.0
    for product in example_sold_products:
        if product['sell_date'].startswith(sell_date_month):
            example_revenue += float(product['sell_price']) * int(product['quantity'])
    revenue = inventory.get_product_revenue(sell_date=sell_date_month)
    assert revenue == round(example_revenue, 2)
    
    ''' Test revenue within a year'''
    sell_date_year = sell_date[0:4:]
    example_revenue = 0.0
    for product in example_sold_products:
        if product['sell_date'].startswith(sell_date_year):
            example_revenue += float(product['sell_price']) * int(product['quantity'])
    revenue = inventory.get_product_revenue(sell_date=sell_date_year)
    assert revenue == round(example_revenue, 2)


def test_inventory_get_product_cost(example_config,
                                    example_bought_csv_file,
                                    example_bought_products):
    ''' Test cost of all products '''
    example_cost = 0.0
    for product in example_bought_products:
        example_cost += float(product['buy_price']) * int(product['quantity'])
    cost = inventory.get_product_cost()
    assert cost == round(example_cost, 2)
    
    ''' Test cost with a product name '''
    example_product = example_bought_products[0]
    product_name = example_product["name"]
    example_cost = 0.0
    for product in example_bought_products:
        if product['name'] == product_name:
            example_cost += float(product['buy_price']) * int(product['quantity'])
    cost = inventory.get_product_cost(product_name=product_name)
    assert cost == round(example_cost, 2)
    
    ''' Test cost on a specific date '''
    buy_date = example_product["buy_date"]
    example_cost = 0.0
    for product in example_bought_products:
        if product['buy_date'] == buy_date:
            example_cost += float(product['buy_price']) * int(product['quantity'])
    cost = inventory.get_product_cost(buy_date=buy_date)
    assert cost == round(example_cost, 2)
    
    ''' Test cost within a month'''
    buy_date_month = buy_date[0:7:]
    example_cost = 0.0
    for product in example_bought_products:
        if product['buy_date'].startswith(buy_date_month):
            example_cost += float(product['buy_price']) * int(product['quantity'])
    cost = inventory.get_product_cost(buy_date=buy_date_month)
    assert cost == round(example_cost, 2)
    
    ''' Test cost within a year'''
    buy_date_year = buy_date[0:4:]
    example_cost = 0.0
    for product in example_bought_products:
        if product['buy_date'].startswith(buy_date_year):
            example_cost += float(product['buy_price']) * int(product['quantity'])
    cost = inventory.get_product_cost(buy_date=buy_date_year)
    assert cost == round(example_cost, 2)


def test_inventory_get_product_profit(example_config,
                                      example_bought_csv_file,
                                      example_bought_products,
                                      example_sold_csv_file,
                                      example_sold_products):
    ''' Test overall profit. '''
    example_revenue = 0.0
    for product in example_sold_products:
        example_revenue += float(product['sell_price']) * int(product['quantity'])
    example_cost = 0.0
    for product in example_bought_products:
        example_cost += float(product['buy_price']) * int(product['quantity'])
    example_profit = example_revenue - example_cost
    profit = inventory.get_product_profit()
    assert profit == round(example_profit, 2)
    
    ''' Test profit for a specific product. '''
    example_product = example_bought_products[0]
    product_name = example_product['name']
    example_revenue = sum([
        (float(product['sell_price']) * int(product['quantity'])) 
        for product in example_sold_products if product['name'] == product_name
    ])
    example_cost = sum([
        (float(product['buy_price']) * int(product['quantity']))
        for product in example_bought_products if product['name'] == product_name
    ])
    example_profit = example_revenue - example_cost
    profit = inventory.get_product_profit(product_name=product_name)
    assert profit == round(example_profit, 2)
    
    ''' Test profit for a specific date. '''
    profit_date = example_product['buy_date']
    example_revenue = sum([
        (float(product['sell_price']) * int(product['quantity']))
        for product in example_sold_products if product['sell_date'] == profit_date
    ])
    example_cost = sum([
        (float(product['buy_price']) * int(product['quantity']))
        for product in example_bought_products if product['buy_date'] == profit_date
    ])
    example_profit = example_revenue - example_cost
    profit = inventory.get_product_profit(profit_date=profit_date)
    assert profit == round(example_profit, 2)
    
    ''' Test profit for a month. '''
    profit_date_month = profit_date[0:7:]
    example_revenue = sum([
        (float(product['sell_price']) * int(product['quantity']))
        for product in example_sold_products if product['sell_date'].startswith(profit_date_month)
    ])
    example_cost = sum([
        (float(product['buy_price']) * int(product['quantity']))
        for product in example_bought_products if product['buy_date'].startswith(profit_date_month)
    ])
    example_profit = example_revenue - example_cost
    profit = inventory.get_product_profit(profit_date=profit_date_month)
    assert profit == round(example_profit, 2)
    
    ''' Test profit for a year. '''
    profit_date_year = profit_date[0:4:]
    example_revenue = sum([
        (float(product['sell_price']) * int(product['quantity']))
        for product in example_sold_products if product['sell_date'].startswith(profit_date_year)
    ])
    example_cost = sum([
        (float(product['buy_price']) * int(product['quantity']))
        for product in example_bought_products if product['buy_date'].startswith(profit_date_year)
    ])
    example_profit = example_revenue - example_cost
    profit = inventory.get_product_profit(profit_date=profit_date_year)
    assert profit == round(example_profit, 2)
    

def test_report_filter_product_properties(example_bought_products):
    ''' Test met gebruikte producteigenschappen zoals gebruikt in de csv header. '''
    example_filter = ['name', 'buy_date', 'expiration_date']
    example_filtered_data = [
        {
            "name": product["name"],
            "buy_date" : product["buy_date"],
            "expiration_date" : product["expiration_date"]
        } for product in example_bought_products
    ]
    test_products = report.filter_product_properties(products=example_bought_products,
                                                     property_filter=example_filter)
    assert test_products == example_filtered_data

    ''' Test met gebruikte producteigenschappen zoals gebruikt in de commandline. '''
    example_filter = ['Name', 'Buy Date', 'Expiration Date']
    test_products = report.filter_product_properties(products=example_bought_products,
                                                     property_filter=example_filter)
    assert test_products == example_filtered_data


def test_report_format_header():
    example_header = ['Id','Name', 'Buy Date','Buy Price', 'Quantity','Expiration Date']
    test_header = report.format_header(example_header)
    assert example_header == test_header


def test_report_product_table(example_bought_products, capsys):
    
    ''' Test met alle kolommen actief. '''    
    report.product_table(products=example_bought_products)
    captured = capsys.readouterr()
    captured_data = (captured.out).split('\n')
    captured_data = [list(map(str.strip, item.split('|')[1:7])) for item in captured_data if not item.startswith('+')]
    example_data = [list(item.values()) for item in example_bought_products]
    assert captured_data[1:-2] == example_data

    ''' Test with filtered columns. '''
    example_filter = ['id','name']
    report.product_table(products=example_bought_products, filter=example_filter)
    captured_data = (capsys.readouterr().out).split('\n')
    captured_data = [list(map(str.strip, item.split('|')))[1:3] for item in captured_data if not item.startswith('+')]
    example_data = [list(item.values())[0:2] for item in example_bought_products]
    assert captured_data[1:-3] == example_data
