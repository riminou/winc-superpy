import os
import csv
import json
import xml.etree.ElementTree as ET


def read_csv(csv_file: str):
    '''
    Functie voor het uitlezen van een csv bestand.
        csv_file = het csv bestand welke uitgelezen dient te worden
    '''
    csv_data = []
    try:
        if (os.path.exists(csv_file)):
            csv_data = []
            with open(csv_file) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    csv_data.append(row)
    except Exception as e:
        print("ERROR: Unable to read data from '{}'.".format(csv_file))
        print(e)
    return csv_data


def write_csv(content: dict, csv_file: str, append:bool=True):
    '''
    Functie voor het schrijven naar een csv bestand.
        content = een dict object die weggeschreven dient te worden
        csv_file = het csv bestand waar naartoe geschreven dient te worden
        append = Indien True worden de content als nieuwe regel toegevoegd,
            Indien False wordt de csv leeggemaakt en de content toegevoegd.
    '''
    try:
        fieldnames = content.keys()
        csv_file = os.path.abspath(csv_file)
        csv_file_dir = os.path.dirname(csv_file)
        if (not (os.path.exists(csv_file))):
            if (not (os.path.exists(csv_file_dir))):
                os.makedirs(csv_file_dir)
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
                writer.writeheader()
        if (append):
            with open(csv_file, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
                writer.writerow(content)
        else:
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(content)
        return True
    except Exception as e:
        print("ERROR: Unable to write data to '{}'".format(csv_file))
        print(e)
    return False


def write_json(product_list:list, json_file:str):
    '''
    Functie voor het schrijven naar een json bestand.
        product_list = een list met producten die weggeschreven dient te worden
        json_file = het json bestand waar naartoe geschreven dient te worden
    '''
    try:
        json_file = os.path.abspath(json_file)
        json_file_dir = os.path.dirname(json_file)
        if (not (os.path.exists(json_file_dir))):
            if (not (os.path.exists(json_file_dir))):
                os.makedirs(json_file_dir)
        with open(json_file, "w") as jsonfile:
            json.dump(product_list, jsonfile, indent=4)
        return True
    except Exception as e:
        print("ERROR: Unable to write data to '{}'".format(json_file))
        print(e)
    return False


def read_json(json_file):
    '''
    Functie voor het uitlezen van een json bestand.
        json_file = het json bestand waar naartoe geschreven dient te worden
    '''
    json_data = []
    try:
        if (os.path.exists(json_file)):
            with open(json_file, 'r') as jsonfile:
                json_data = json.load(jsonfile)
    except Exception as e:
        print("ERROR: Unable to read data from '{}'.".format(json_file))
        print(e)
    return json_data


def write_xml(product_list:list, xml_file:str):
    ''' Functie voor het schrijven naar xml. '''
    try:
        xml_file = os.path.abspath(xml_file)
        xml_file_dir = os.path.dirname(xml_file)
        if (not (os.path.exists(xml_file_dir))):
            if (not (os.path.exists(xml_file_dir))):
                os.makedirs(xml_file_dir)
        root =  ET.Element('products')
        for product in product_list:
            sub_element = ET.SubElement(root, 'product')
            for product_property in product.keys():
                property_element = ET.SubElement(sub_element, product_property)
                property_element.text = str(product[product_property])
        tree = ET.ElementTree(root)
        ET.indent(tree, space='    ')
        tree.write(xml_file, xml_declaration=True, encoding='utf-8')
        return True
    except Exception as e:
        print("ERROR: Unable to write data to '{}'".format(xml_file))
        print(e)
    return False


def read_xml(xml_file:str):
    ''' Functie voor het uitlezen van een xml. '''
    xml_data = []
    xml_file = os.path.abspath(xml_file)
    if (os.path.exists(xml_file)):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for element in root.iter('product'):
                product = {}
                for child_element in element:
                    product[child_element.tag] = child_element.text
                xml_data.append(product)
        except Exception as e:
            print("ERROR: Unable to read data from '{}'.".format(xml_file))
            print(e)
    else:
        print("ERROR: Xml file '{}' doesn't exist.".format(xml_file))
    return xml_data
