import sys
import argparse

from super import date, buy, sell, create_report, inventory_import, inventory_export, create_chart


def parse():
    parent_parser = argparse.ArgumentParser(description="SuperPy Inventory Manager", add_help=True)
    
    subparsers = parent_parser.add_subparsers(title="SuperPy Inventory Manager")
    
    date_parser = subparsers.add_parser("date",
                                        parents=[parent_parser],
                                        add_help=False,
                                        description="date",
                                        help="Get or set the current date.")
    date_group = date_parser.add_mutually_exclusive_group()
    date_group.add_argument('-ad',
                            '--advance-date',
                            type=int,
                            nargs=1,
                            help='Specify number of days to advance or disadvance.')
    date_group.add_argument('-gd',
                            '--get-date',
                            action='store_true',
                            help='Gets the current time for super.py.')
    date_group.add_argument('-sd',
                            '--set-date',
                            type=str,
                            nargs=1,                           
                            help='Sets the current time for super.py.')
    date_parser.set_defaults(func=date)
    
    buy_parser = subparsers.add_parser("buy",
                                       parents=[parent_parser],
                                       add_help=False,
                                       description="buy",
                                       help="Buy a pruduct.")
    buy_parser.add_argument('-pn',
                            '--product-name',
                            help='Specify the productname.',
                            type=str,
                            required=True)
    buy_parser.add_argument('-p',
                            '--price',
                            help='Specify product price. Use positve prices only.',
                            type=float,
                            required=True)
    buy_parser.add_argument('-qt',
                            '--quantity',
                            help='Specify product quantity to buy.',
                            type=int,
                            default=1,
                            required=False)
    buy_parser.add_argument('-ed',
                            '--expiration-date',
                            help='Specify expiration date of the prodoct. Use the "YYYY-MM-DD" format: -ed 2024-02-04',
                            type=str,
                            required=True)
    buy_parser.set_defaults(func=buy)

    sell_parser = subparsers.add_parser("sell", 
                                        parents=[parent_parser],
                                        add_help=False,
                                        description="sell",
                                        help="Sell a pruduct.")
    sell_parser.add_argument('-pn',
                             '--product-name',
                             help='Specify the productname.',
                             type=str,
                             required=True)
    sell_parser.add_argument('-p',
                             '--price',
                             help='Specify product price.',
                             type=float,
                             required=True)
    sell_parser.add_argument('-qt',
                            '--quantity',
                            help='Specify product quantity to sell.',
                            type=int,
                            default=1,
                            required=False)
    sell_parser.set_defaults(func=sell)
    
    report_parser = subparsers.add_parser("report", help="Create a report.")
    report_parser.add_argument(dest='report_type',
                               help='the type of report to create',
                               choices=['inventory', 'profit', 'revenue', 'cost', 'expired', 'sold'],
                               nargs=1,
                               type=str)
    report_parser.add_argument('-pn',
                               '--product-name',
                               dest='product_name',
                               help='The productname to report, when omitted or empty all products will be reported.',
                               nargs=1,
                               type=str)
    report_parser.add_argument('-e',
                               '--export',
                               dest='export_report',
                               help='The filename to export the report to, supported filetypes are: csv, xml, json.',
                               nargs=1,
                               type=str)
    report_group = report_parser.add_mutually_exclusive_group()
    report_group.add_argument('--now',
                              action='store_true',
                              help='create a report of the date in "current_date" file.')
    report_group.add_argument('--today',
                              action='store_true',
                              help='create a report of today.')
    report_group.add_argument('--yesterday',
                              action='store_true',
                              help='create a report of yesterday.')
    report_group.add_argument('--date',
                              nargs=1,
                              type=str,
                              help='create a report of all products on a specific date, input: "YYYY-MM-dd", "YYYY-MM" or "YYYY"')
    report_parser.set_defaults(func=create_report)
    
    chart_parser = subparsers.add_parser("chart", help="Create a chart.")
    chart_parser.add_argument('-pn',
                               '--product_name',
                               dest='product_name',
                               help='The productname to create chart for, when omitted or empty all products will be displayed in the chart.',
                               nargs=1,
                               type=str)
    chart_parser.add_argument('-d',
                               '--date',
                               dest='date',
                               help='The date to create chart for, input: "YYYY-MM-dd", "YYYY-MM" or "YYYY"',
                               type=str)
    chart_parser.add_argument('-r',
                              '--revenue',
                              action='store_true',
                              help='create a chart of the revenue.')
    chart_parser.add_argument('-p',
                              '--profit',
                              action='store_true',
                              help='create a chart of the profit.')
    chart_parser.add_argument('-c',
                              '--cost',
                              action='store_true',
                              help='create a chart of the costs.')
    chart_parser.set_defaults(func=create_chart)
    
    inventory_parser = subparsers.add_parser("inventory", help="Manage inventory.")
    inventory_group = inventory_parser.add_mutually_exclusive_group()
    inventory_group.add_argument('--import',
                               type=inventory_import,
                               dest='file',
                               help='Specify a file to import bought products from [csv, json, xml]')
    inventory_group.add_argument('--export',
                               type=inventory_export,
                               dest='file',
                               help='Specify a file to export bought products to [csv, json, xml]')
    
    parent_args = parent_parser.parse_args()
    
    if len(vars(parent_args)) > 0:
        if 'func' in vars(parent_args): 
            return_value = parent_args.func(parent_args)
            return return_value
    else:
        parent_parser.print_help(sys.stderr)
