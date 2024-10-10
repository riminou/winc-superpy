from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich import box
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

import superpy.config as config
from superpy.convert import date_str_to_datetime


def filter_product_properties(products:list, property_filter:list):
    ''' 
    Functie voor het toepassen van een filter voor de producteigenschappen 
    die getoond dienen te worden in het voorraad overzicht.
        products = een list met producten
        property_filter = een list met producteigenschappen
    '''
    if len(property_filter) > 0:
        product_property_list = []
        property_filter = [item.replace(" ", "_").lower() for item in property_filter]
        for product_property in products[0].keys():
            if product_property.lower() in property_filter:
                product_property_list.append(product_property)
        if len(product_property_list) > 0:
            new_product_list = []
            for product in products:
                filtered_product = {}
                for product_property in product_property_list:
                    filtered_product[product_property] = product[product_property]
                new_product_list.append(filtered_product)
            return new_product_list
    return products


def format_header(header_values:list):
    '''
    Functie voor het maken van een header voor het voorraad overzicht.
        header_values = een list met waardes voor de header
    '''
    new_header = []
    for header_value in header_values:
        if "_" in header_value:
            header_value = header_value.replace('_', ' ')
        new_header.append(header_value.title())
    return new_header
        

def product_table(products:list, filter:list=[]):
    '''
    Functie voor het genereren van een product tabel.
        products = een list met producten.
        filter = een list met producteigenschappen 
            die niet getoond hoeven te worden.
    '''
    if len(products) > 0:
        total_quantity = sum([int(product['quantity']) for product in products])
        table = Table(box=box.ASCII_DOUBLE_HEAD, caption=f'Total quantity: {total_quantity}')
        products = filter_product_properties(products, filter)
        # create header
        formatted_header = format_header(products[0].keys())
        for column_name in formatted_header:
            table.add_column(column_name, justify="left", no_wrap=True)
        if total_quantity != 0:
            # add rows
            for row_data in products:
                table.add_row(*(row_data.values()))
                table.add_section()
        console = Console()
        console.print(table)


def get_daily_chart_values(chart_type:str,
                           products:list,
                           start_date:str,
                           end_date:str):
    '''
    Functie voor het bepalen van de dagelijkse hoeveelheden
    voor aanmaken van een rapportage.
        chart_type = type grafiek waarvoor de dagelijkse hoeveelheid
            bepaald dient te worden: 'cost' of 'revenue'.
        products = een list van producten.
    '''
    daily_values = {}
    if len(products) > 0:
        chart_products = products.copy()
        date_type = ''
        price_type = ''
        if chart_type == 'cost':
            date_type = 'buy_date'
            price_type= 'buy_price'
        elif chart_type == 'revenue':
            date_type = 'sell_date'
            price_type= 'sell_price'
        start_date = date_str_to_datetime(start_date)
        end_date = date_str_to_datetime(end_date)
        date_format = config.data["date_format"]
        total_value = 0.0
        while start_date <= end_date:
            value_date = datetime.strftime(start_date, date_format)
            for product in chart_products:
                if product[date_type] == value_date:
                    total_value += (int(product['quantity']) * float(product[price_type]))
                    chart_products.remove(product)
            if value_date in daily_values.keys():
                daily_values[value_date] += round(total_value, 2)
            else:
                daily_values[value_date] = round(total_value, 2)
            start_date += timedelta(days=1)
    return daily_values


def get_start_and_end_date(products:list, date_type:str):
    start_date = ''
    end_date = ''
    if len(products) > 0:
        sorted_products = sorted(products, key=lambda x: x[date_type])
        start_date = sorted_products[0][date_type]
        sorted_products.reverse()
        end_date = sorted_products[0][date_type]
    return start_date, end_date


def get_start_date(start_buy_date:str,
                   start_sell_date:str):
    start_date = ''
    if start_buy_date == '':
        start_date = start_sell_date
    elif start_sell_date == '':
        start_date = start_buy_date
    elif start_buy_date < start_sell_date:
        start_date = start_buy_date
    else:
        start_date = start_sell_date
    return start_date


def get_end_date(end_buy_date:str,
                 end_sell_date:str):
    end_date = ''
    if end_buy_date == '':
        end_date = end_sell_date
    elif end_sell_date == '':
        end_date = end_buy_date
    elif end_buy_date > end_sell_date:
        end_date = end_buy_date
    else:
        end_date = end_sell_date
    return end_date


CHART_TYPES = ['cost','revenue','profit']

def product_chart(chart_types:list,
                  bought_products:list=[],
                  sold_products:list=[]):
    '''
    Functie voor het maken van een product grafiek.
        chart_types = list met de type grafieken die 
            getoond dienen te worden.
        bought_products = list met gekochte producten voor
            het maken van een kosten grafiek.
        sold_products = list met verkochte producten voor
            het maken van een omzet grafiek.
    '''
    charts = {}
    start_buy_date, end_buy_date = get_start_and_end_date(products=bought_products,
                                                          date_type='buy_date')
    start_sell_date, end_sell_date = get_start_and_end_date(products=sold_products,
                                                          date_type='sell_date')
    start_date = get_start_date(start_buy_date=start_buy_date,
                                start_sell_date=start_sell_date)
    end_date = get_end_date(end_buy_date=end_buy_date,
                            end_sell_date=end_sell_date)
    if 'cost' in chart_types:
        costs = get_daily_chart_values(chart_type='cost',
                                       products=bought_products,
                                       start_date=start_date,
                                       end_date=end_date)
        charts['Daily Cost'] = costs
    if 'revenue' in chart_types:
        revenues = get_daily_chart_values(chart_type='revenue',
                                          products=sold_products,
                                          start_date=start_date,
                                          end_date=end_date)
        charts['Daily Revenue'] = revenues
    if 'profit' in chart_types:
        profit_costs = get_daily_chart_values(chart_type='cost',
                                              products=bought_products,
                                              start_date=start_date,
                                              end_date=end_date)
        profit_revenues = get_daily_chart_values(chart_type='revenue',
                                                 products=sold_products,
                                                 start_date=start_date,
                                                 end_date=end_date)
        profits = {}
        for date in profit_costs.keys():
            cost = profit_costs[date]
            revenue = profit_revenues[date]
            profit = revenue - cost
            profits[date] = round(profit, 2)
        charts['Daily Profits'] = profits
    if len(charts) > 0:
        for chart in charts.keys():
            x_values = list(charts[chart].keys())
            y_values = list(charts[chart].values())
            plt.plot(x_values, y_values, label=chart)
        plt.tick_params(axis='x', labelrotation=90)
        plt.xlabel('Dates')
        plt.ylabel('Amount')
        plt.title('Super.py Report')
        plt.legend()
        plt.grid(True)
        plt.show()
        return True
    else:
        print('ERROR: No data available for chart creation.')
    return False
