# Imports
import superpy.args as args
import superpy.config as config
import superpy.inventory as inventory
import superpy.report as report
import superpy.current_date as current_date
import superpy.validate as validate
import superpy.convert as convert


# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"


# Your code below this line.


CONFIG_FILE = "config.json"


def date(args):
    if args.get_date:
        print(f'The current super.py date is "{current_date.get()}"')
    elif args.set_date:
        if validate.date_format(args.set_date[0]):
            current_date.set(args.set_date[0])
            print(f'The new super.py date is "{current_date.get()}"')
    elif args.advance_date:
        new_date = current_date.advance(args.advance_date[0])
        if new_date:
            print(f'The new super.py date is "{current_date.get()}"')


def buy(args):
    if inventory.buy(product_name=args.product_name,
                     price=args.price,
                     quantity=args.quantity,
                     expiration_date=args.expiration_date):
        print('OK')
    else:
        print('NOK')


def sell(args):
    if inventory.sell(product_name=args.product_name,
                      price=args.price,
                      quantity=args.quantity):
        print('OK')
    else:
        print('NOK')


def create_report(args):
    report_date = ''
    product_name = ''
    if args.product_name != None:
        product_name = args.product_name[0]
    if args.today:
        report_date = current_date.today()
        revenue_message = "Today's revenue so far: "
        profit_message = "Today's profit so far: "
        cost_message = "Today's costs so far: "
    elif args.now:
        report_date = current_date.get()
        revenue_message = "Today's revenue so far: "
        profit_message = "Today's profit so far: "
        cost_message = "Today's costs so far: "
    elif args.yesterday:
        report_date = current_date.advance(days=-1)
        revenue_message = "Yesterday's revenue: "
        profit_message = "Yesterday's profit: "
        cost_message = "Yesterday's costs: "
    elif args.date != None:
        report_date = args.date[0]
        report_date_text = convert.date_str_to_text(args.date[0])
        revenue_message = f"Revenue from {report_date_text}: "
        profit_message = f"Profit from {report_date_text}: "
        cost_message = f"Costs from {report_date_text}: "
    if validate.date_format(report_date):
        products = []
        if args.report_type[0] == 'inventory':
            products, quantity = inventory.get_available_products(product_name=product_name,
                                                                  product_date=report_date)
            report.product_table(products)
        elif args.report_type[0] == 'sold':
            products, quantity = inventory.get_sold_products(product_name=product_name,
                                                             sell_date=report_date)
            report.product_table(products)
        elif args.report_type[0] == 'expired':
            products = inventory.get_expired_products(product_name=product_name,
                                                      product_date=report_date)
            report.product_table(products)
        elif args.report_type[0] == 'revenue':
            revenue = inventory.get_product_revenue(product_name=product_name,
                                                    sell_date=report_date)
            print(revenue_message + str(revenue))
        elif args.report_type[0] == 'profit':
            profit = inventory.get_product_profit(product_name=product_name,
                                                  profit_date=report_date)
            print(profit_message + str(profit))
        elif args.report_type[0] == 'cost':
            cost = inventory.get_product_cost(product_name=product_name,
                                              buy_date=report_date)
            print(cost_message + str(cost))
        
        if args.export_report != None and len(products) > 0:
            if int(products[0]['quantity']) > 0:
                inventory.export_products_to_file(file=args.export_report[0],
                                                  products=products)
    if args.yesterday:
        report_date = current_date.advance(days=1)


def create_chart(args):
    chart_date = ''
    product_name = ''
    chart_types = []
    bought_products = []
    sold_products = []
    if args.product_name != None:
        product_name = args.product_name[0]
    if args.date != None:
        chart_date = args.date
    if args.cost:
        bought_products, bought_quantity = inventory.get_bought_products(product_name=product_name,
                                                                         buy_date=chart_date)
        chart_types += ['cost']
    if args.revenue:
        sold_products, sold_quantity = inventory.get_sold_products(product_name=product_name,
                                                                   sell_date=chart_date)
        chart_types += ['revenue']
    if args.profit:
        bought_products, bought_quantity = inventory.get_bought_products(product_name=product_name,
                                                                         buy_date=chart_date)
        sold_products, sold_quantity = inventory.get_sold_products(product_name=product_name,
                                                                   sell_date=chart_date)
        chart_types += ['profit']
    print(f'Creating chart for {", ".join(chart_types)}...')
    if not report.product_chart(chart_types=chart_types,
                                bought_products=bought_products,
                                sold_products=sold_products):
        print('ERROR: Failed to create chart.')


def inventory_import(file):
    if not inventory.import_products_from_file(file):
        print('ERROR: Import failed.')


def inventory_export(file):
    if inventory.export_products_to_file(file):
        print('OK')
    print('ERROR: Export failed.')


def main():
    args.parse()


if __name__ == "__main__":
    if (config.init_config(CONFIG_FILE)):
        main()
    else:
        print("ERROR: No valid config found.")
