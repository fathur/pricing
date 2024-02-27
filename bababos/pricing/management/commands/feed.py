import csv
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils import timezone

from bababos.pricing.models import Customer, Logistic, Product, Region, Supplier


class Command(BaseCommand):
    help = "Feed initial data"

    regions = {
        "DKI Jakarta": {
            "Kota Jakarta Utara": {"Cilincing": {}},
            "Kota Jakarta Barat": {},
            "Kota Jakarta Selatan": {},
            "Kota Jakarta Pusat": {},
            "Kota Jakarta Timur": {},
        },
        "Jawa Barat": {
            "Kabupaten Bekasi": {
                "Cikarang": {},  # Actually, there are five areas
                "Cikarang Selatan": {},
            },
            "Kabupaten Bogor": {"Gunung Sindur": {}},
            "Kota Bogor": {},
            "Kota Depok": {},
        },
        "Jawa Timur": {
            "Kota Surabaya": {},
            "Kabupaten Sidoarjo": {},
            "Kabupaten Gresik": {},
        },
        "Banten": {
            "Kabupaten Tangerang": {},
            "Kota Tangerang": {},
            "Kota Tangerang Selatan": {},
        },
    }

    logistics = [
        ["Fuso", 8],
        ["Tronton", 22],
    ]

    logistic_prices = {
        "Fuso": [
            ["Kota Jakarta Timur", 1.6],
            ["Kota Jakarta Barat", 1.6],
            ["Kota Jakarta Utara", 1.6],
            ["Kota Jakarta Selatan", 1.6],
            ["Kabupaten Bekasi", 1.8],
            ["Kota Depok", 1.8],
            ["Cikarang", 1.8],
            ["Gunung Sindur", 1.9],
            ["Kabupaten Tangerang", 1.8],
        ],
        "Tronton": [
            ["Kota Jakarta Timur", 2.5],
            ["Kota Jakarta Barat", 2.5],
            ["Kota Jakarta Utara", 2.5],
            ["Kota Jakarta Selatan", 2.5],
            ["Kabupaten Bekasi", 3.45],
            ["Kota Depok", 3.45],
            ["Cikarang", 3.45],
            ["Gunung Sindur", 3.46],
            ["Kabupaten Tangerang", 3.45],
        ],
    }

    def handle(self, *args, **options):
        self.feed_regions()
        self.feed_customers()
        self.feed_suppliers()
        self.feed_logistics()
        self.feed_logistic_prices()
        self.feed_customer_request_for_quotations()
        self.feed_pricelist()
        self.feed_purchase_orders()

        self.delete_unused_suppliers()

    def feed_regions(self):
        """
        This function will not work in migrations, due to issue with mppt library,
        run this function manually in django shell.
        """
        from bababos.pricing.models import Region

        for province in self.regions:
            province_instance = self._find_or_create_if_not_exists(
                Region, province, root=True
            )
            for city in self.regions[province]:
                city_instance = self._find_or_create_if_not_exists(
                    province_instance, city
                )
                for district in self.regions[province][city]:
                    self._find_or_create_if_not_exists(city_instance, district)

    @staticmethod
    def feed_customers():

        with open("resources/customer.csv", newline="") as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)
            for row in reader:
                if User.objects.filter(username=row[0].lower()).exists():
                    continue

                user = User.objects.create(username=row[0].lower())
                region = Region.objects.get(name=row[2])

                # todo: simplify using 1 to 1 relationship
                Customer.objects.create(
                    user=user, code=row[0], address=row[1], region=region
                )

    @staticmethod
    def feed_suppliers():

        with open("resources/supplier.csv", newline="") as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)

            for row in reader:
                if User.objects.filter(username=row[0].lower()).exists():
                    continue
                user = User.objects.create(username=row[0].lower())
                region = Region.objects.get(name=row[2])

                # todo: simplify using 1 to 1 relationship
                Supplier.objects.create(
                    user=user, code=row[0], address=row[1], region=region
                )

    def feed_logistics(self):

        for logistic in self.logistics:
            if Logistic.objects.filter(fleet_type=logistic[0]).exists():
                continue
            Logistic.objects.create(fleet_type=logistic[0], capacity=logistic[1])

    def feed_logistic_prices(self):

        for item in self.logistic_prices:
            logistic = Logistic.objects.filter(fleet_type=item).last()
            for dst_price in self.logistic_prices[item]:
                _price = dst_price[1] * (10**6)
                _src = Region.objects.get(name="Cilincing")
                _dst = Region.objects.get(name=dst_price[0])

                if logistic.prices.filter(source=_src, destination=_dst).exists():
                    continue

                logistic.prices.create(source=_src, destination=_dst, price=_price)

    @staticmethod
    def feed_customer_request_for_quotations():

        with open("resources/rfq-customer.csv", newline="") as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)

            for row in reader:
                customer = Customer.objects.get(code=row[0])

                product = Product.objects.filter(sku=row[1]).last()
                if product is None:
                    product = Product.objects.create(sku=row[1])

                customer.RFQs.create(
                    product=product,
                    quantity=row[2],
                    unit=row[3],
                )

    @staticmethod
    def feed_pricelist():

        with open("resources/pricelist.csv", newline="") as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)

            for row in reader:
                supplier = Supplier.objects.get(code=row[0])
                product = Product.objects.filter(sku=row[1]).last()
                if product is None:
                    product = Product.objects.create(sku=row[1])

                supplier.prices.create(
                    product=product, price=row[2], available_stock=row[3]
                )

    @staticmethod
    def feed_purchase_orders():

        with open("resources/historical-po.csv", newline="") as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)

            for row in reader:
                customer = Customer.objects.get(code=row[0])
                product = Product.objects.get(sku=row[3])
                if product.name is None:
                    product.name = row[4]
                    product.save()

                customer.POs.create(
                    product=product,
                    quantity=int(row[5]),
                    ordered_at=timezone.make_aware(
                        datetime.strptime(row[1], "%d/%m/%Y")
                    ),
                    unit=row[6],
                    price=float(row[7]),
                )

    @staticmethod
    def _find_or_create_if_not_exists(model, region, root=False):
        if root:
            instance = model.objects.filter(name=region).last()
        else:
            instance = model.children.filter(name=region).last()

        if instance:
            return instance

        if root:
            return model.objects.create(name=region)

        return model.children.create(name=region)

    @staticmethod
    def delete_unused_suppliers():
        Supplier.objects.filter(
            code__in=[
                "S1-JAY-1",
                "S1-BJS-1",
                "S1-BJN-1",
                "S1-SIE-1",
                "S1-PER-1",
                "S1-KKP-1",
                "S1-BUS-1",
                "S1-WAB-1",
                "S1-AIT-1",
                "S1-DBT-1",
                "S1-LCI-1",
                "S1-SUL-1",
                "S1-IWP-1",
                "S1-WIR-1",
                "S1-KWS-1",
                "S1-ZUG-1",
            ]
        ).delete()
