import csv
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils import timezone
from tabulate import tabulate

from bababos.pricing.models import Customer, Logistic, Product, Region, Supplier, RFQ
from colorama import init, Fore, Style


class Command(BaseCommand):
    help = "Analyze"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

        self.rfq = None

    def add_arguments(self, parser):
        parser.add_argument("rfq_id", nargs="?", type=int)

    def handle(self, *args, **options):
        init()

        rfq_id = options["rfq_id"]

        self.rfq = RFQ.objects.get(pk=rfq_id)
        self.print_rfq_table()
        self.print_customer_purchase_order_histories()
        self.print_supplier_prices()
        self.print_transactions()

    def print_rfq_table(self):
        self.stdout.write("\n## RFQ (Request for Quotation)")
        self.stdout.write(
            tabulate(
                [
                    ["ID", self.rfq.id],
                    ["customer", self.rfq.customer.code],
                    ["product", self.rfq.product.sku],
                    [
                        "quantity",
                        Fore.RED
                        + Style.BRIGHT
                        + str(self.rfq.quantity)
                        + Style.RESET_ALL,
                    ],
                    ["unit", self.rfq.unit],
                ],
                tablefmt="github",
            )
        )

    def print_customer_purchase_order_histories(self):
        customer = self.rfq.customer
        purchase_orders = customer.POs.filter(product=self.rfq.product)

        data = []
        for purchase_order in purchase_orders:
            data.append(
                [
                    purchase_order.id,
                    purchase_order.ordered_at,
                    f"{purchase_order.quantity} {purchase_order.unit}",
                    self.format_currency(purchase_order.price),
                    purchase_order.customer.code,
                    purchase_order.product.sku,
                ]
            )

        self.stdout.write("\n## PO Histories")
        self.stdout.write(
            tabulate(
                data,
                headers=[
                    "ID",
                    "Ordered At",
                    "Quantity",
                    "Price",
                    "Customer",
                    "Product",
                ],
                tablefmt="pretty",
            )
        )

    @staticmethod
    def format_currency(amount, currency="IDR"):
        from babel.numbers import format_currency

        formatted_amount = format_currency(amount, currency, locale="id_ID")
        return formatted_amount

    def print_supplier_prices(self):
        product = self.rfq.product
        supplier_prices = product.supplier_prices.order_by("price")
        data = []
        for supplier_price in supplier_prices:
            data.append(
                [
                    supplier_price.id,
                    supplier_price.supplier.code,
                    Fore.YELLOW
                    + Style.BRIGHT
                    + str(supplier_price.available_stock)
                    + Style.RESET_ALL,
                    self.format_currency(supplier_price.price),
                ]
            )
        self.stdout.write("\n## Supplier Prices")
        self.stdout.write(
            tabulate(
                data,
                headers=["ID", "Supplier", "Available Stock", "Price"],
                tablefmt="psql",
            )
        )

    def print_transactions(self):
        transactions = self.rfq.transactions.all()
        data = []
        for transaction in transactions:
            data.append(
                [
                    transaction.id,
                    Fore.CYAN + str(transaction.quantity) + Style.RESET_ALL,
                    transaction.supplier_price.id,
                    self.format_currency(transaction.supplier_price.price),
                    self.format_currency(transaction.chosen_price),
                    "{} %".format(round(transaction.analyzed_profit_margin * 100, 2)),
                    Fore.BLUE
                    + Style.BRIGHT
                    + self.format_currency(transaction.final_price)
                    + Style.RESET_ALL,
                    transaction.supplier_price.supplier.code,
                    transaction.status,
                    # transaction.note
                ]
            )
        self.stdout.write("\n## Transactions")
        self.stdout.write(
            tabulate(
                data,
                headers=[
                    "ID",
                    "Quantity",
                    "Supplier Price ID",
                    "Supplier Price",
                    "Chosen Price",
                    "Profit Margin",
                    "Final Price",
                    "Supplier",
                    "Status",
                    # "Note"
                ],
                tablefmt="presto",
            )
        )
