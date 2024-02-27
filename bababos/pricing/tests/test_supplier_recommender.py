import pytest
from django.test import TestCase
from parameterized import parameterized
from decimal import getcontext, Decimal

from bababos.pricing.models import (
    CustomerFactory,
    POFactory,
    ProductFactory,
    RFQFactory,
    SupplierFactory,
    SupplierPriceFactory,
)
from bababos.pricing.services.supplier_recommender import RFQAnalyzer


class TestRFQAnalyzer(TestCase):
    def setUp(self) -> None:
        self.product = ProductFactory()
        self.customer = CustomerFactory()

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "price": 730_000, "final_price": 916_329.03},
                {
                    "po": {"qty": 500},
                    "sup": {"stock": 500},
                },
            ),
            (
                {"rfq_qty": 5, "price": 900_000, "final_price": 1_348_234.23},
                {
                    "po": {"qty": 5},
                    "sup": {"stock": 5},
                },
            ),
            (
                {"rfq_qty": 990, "price": 300_000, "final_price": 304_471.47},
                {
                    "po": {"qty": 990},
                    "sup": {"stock": 990},
                },
            ),
        ]
    )
    def test_one_po_history_and_one_candidate_supplier_has_same_price(
        self, conf, param
    ):
        POFactory(
            customer=self.customer,
            product=self.product,
            quantity=param["po"]["qty"],
            price=conf["price"],
        )
        rfq = RFQFactory(
            customer=self.customer, product=self.product, quantity=conf["rfq_qty"]
        )
        supplier = SupplierFactory()
        SupplierPriceFactory(
            supplier=supplier,
            product=self.product,
            price=conf["price"],
            available_stock=param["sup"]["stock"],
        )

        analyzer = RFQAnalyzer(rfq).handle()

        self.assertEqual(analyzer.chosen_price, conf["price"])

        # If a customer buys the same price as supplier, then no profit for the company.
        # Add profit margin.
        self.assertGreaterEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MIN_PROFIT
        )
        self.assertLessEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MAX_PROFIT
        )
        self.assertGreater(analyzer.final_price, conf["price"])
        # self.assertEqual(float(round(analyzer.final_price, 2)), conf["final_price"])

    @parameterized.expand(
        [
            (
                {
                    "rfq_qty": 500,
                },
                {
                    "po": {"qty": 500, "price": 800_000},
                    "sup": {"price": 730_000, "stock": 500},
                },
            ),
            (
                {
                    "rfq_qty": 5,
                },
                {
                    "po": {"qty": 5, "price": 750_000},
                    "sup": {"price": 730_000, "stock": 5},
                },
            ),
            (
                {
                    "rfq_qty": 990,
                },
                {
                    "po": {"qty": 990, "price": 740_000},
                    "sup": {"price": 730_000, "stock": 990},
                },
            ),
        ]
    )
    def test_one_po_history_has_higher_price_than_one_candidate_supplier(
        self, conf, param
    ):
        POFactory(
            customer=self.customer,
            product=self.product,
            quantity=param["po"]["qty"],
            price=param["po"]["price"],
        )
        rfq = RFQFactory(
            customer=self.customer, product=self.product, quantity=conf["rfq_qty"]
        )
        supplier = SupplierFactory()
        SupplierPriceFactory(
            supplier=supplier,
            product=self.product,
            price=param["sup"]["price"],
            available_stock=param["sup"]["stock"],
        )

        analyzer = RFQAnalyzer(rfq).handle()

        self.assertEqual(analyzer.chosen_price, param["sup"]["price"])

        # If po history higher than supplier pricing, give the price the same as previous history.
        # With the consequence, the profit is not like profit margin formula.
        self.assertGreaterEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MIN_PROFIT
        )
        self.assertLessEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MAX_PROFIT
        )
        # self.assertEqual(float(round(analyzer.final_price, 2)), param["po"]["price"])

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 916_329.03},
                {
                    "po": {"qty": 500, "price": 700_000},
                    "sup": {"price": 730_000, "stock": 500},
                },
            ),
            (
                {"rfq_qty": 5, "final_price": 1_093_567.77},
                {
                    "po": {"qty": 5, "price": 700_000},
                    "sup": {"price": 730_000, "stock": 5},
                },
            ),
            (
                {"rfq_qty": 1000, "final_price": 737_300},
                {
                    "po": {"qty": 1000, "price": 700_000},
                    "sup": {"price": 730_000, "stock": 1000},
                },
            ),
        ]
    )
    def test_one_po_history_has_lower_price_than_one_candidate_supplier(
        self, conf, param
    ):
        POFactory(
            customer=self.customer,
            product=self.product,
            quantity=param["po"]["qty"],
            price=param["po"]["price"],
        )
        rfq = RFQFactory(
            customer=self.customer, product=self.product, quantity=conf["rfq_qty"]
        )
        supplier = SupplierFactory()
        SupplierPriceFactory(
            supplier=supplier,
            product=self.product,
            price=param["sup"]["price"],
            available_stock=param["sup"]["stock"],
        )

        analyzer = RFQAnalyzer(rfq).handle()

        self.assertEqual(analyzer.chosen_price, param["sup"]["price"])

        # If a customer buys the same price as supplier, then no profit for the company.
        # Add profit margin.
        self.assertGreaterEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MIN_PROFIT
        )
        self.assertLessEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MAX_PROFIT
        )
        # self.assertEqual(float(round(analyzer.final_price, 2)), conf["final_price"])

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 878_671.67},
                {
                    "po": {"qty": 500, "price": 700_000},
                    "sup": [
                        {"price": 700_000, "stock": 300},
                        {"price": 700_000, "stock": 200},
                    ],
                },
            )
        ]
    )
    def test_one_po_history_and_multiple_candidate_suppliers_has_same_price(
        self, conf, param
    ):
        POFactory(
            customer=self.customer,
            product=self.product,
            quantity=param["po"]["qty"],
            price=param["po"]["price"],
        )
        rfq = RFQFactory(
            customer=self.customer, product=self.product, quantity=conf["rfq_qty"]
        )
        for sup in param["sup"]:
            supplier = SupplierFactory()
            SupplierPriceFactory(
                supplier=supplier,
                product=self.product,
                price=sup["price"],
                available_stock=sup["stock"],
            )

        analyzer = RFQAnalyzer(rfq).handle()

        self.assertEqual(analyzer.chosen_price, param["po"]["price"])
        self.assertGreaterEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MIN_PROFIT
        )
        self.assertLessEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MAX_PROFIT
        )
        self.assertGreater(analyzer.final_price, analyzer.chosen_price)
        # self.assertEqual(float(round(analyzer.final_price, 2)), conf["final_price"])

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 880_000},
                {
                    "po": {"qty": 500, "price": 800_000},
                    "sup": [
                        {"price": 730_000, "stock": 300},
                        {"price": 750_000, "stock": 200},
                    ],
                },
            )
        ]
    )
    def test_one_po_history_has_higher_price_than_multiple_candidate_suppliers(
        self, conf, param
    ):
        POFactory(
            customer=self.customer,
            product=self.product,
            quantity=param["po"]["qty"],
            price=param["po"]["price"],
        )
        rfq = RFQFactory(
            customer=self.customer, product=self.product, quantity=conf["rfq_qty"]
        )
        for sup in param["sup"]:
            supplier = SupplierFactory()
            SupplierPriceFactory(
                supplier=supplier,
                product=self.product,
                price=sup["price"],
                available_stock=sup["stock"],
            )

        analyzer = RFQAnalyzer(rfq).handle()

        self.assertEqual(analyzer.chosen_price, param["po"]["price"])
        self.assertGreaterEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MIN_PROFIT
        )
        self.assertLessEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MAX_PROFIT
        )
        # self.assertEqual(round(analyzer.final_price, 2), round(analyzer.chosen_price, 2))
        self.assertEqual(float(round(analyzer.final_price, 2)), conf["final_price"])

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 941_433.93},
                {
                    "po": {"qty": 500, "price": 700_000},
                    "sup": [
                        {"price": 730_000, "stock": 300},
                        {"price": 750_000, "stock": 200},
                    ],
                },
            ),
            (
                {"rfq_qty": 3, "final_price": 1_124_264.26},
                {
                    "po": {"qty": 3, "price": 700_000},
                    "sup": [
                        {"price": 730_000, "stock": 2},
                        {"price": 750_000, "stock": 1},
                    ],
                },
            ),
            (
                {"rfq_qty": 1000, "final_price": 757_500},
                {
                    "po": {"qty": 1000, "price": 700_000},
                    "sup": [
                        {"price": 730_000, "stock": 600},
                        {"price": 750_000, "stock": 400},
                    ],
                },
            ),
        ]
    )
    def test_one_po_history_has_lower_price_than_multiple_candidate_suppliers(
        self, conf, param
    ):
        POFactory(
            customer=self.customer,
            product=self.product,
            quantity=param["po"]["qty"],
            price=param["po"]["price"],
        )
        rfq = RFQFactory(
            customer=self.customer, product=self.product, quantity=conf["rfq_qty"]
        )
        max_sup_price = 0
        for sup in param["sup"]:
            supplier = SupplierFactory()
            SupplierPriceFactory(
                supplier=supplier,
                product=self.product,
                price=sup["price"],
                available_stock=sup["stock"],
            )
            if sup["price"] > max_sup_price:
                max_sup_price = sup["price"]

        analyzer = RFQAnalyzer(rfq).handle()

        self.assertEqual(analyzer.chosen_price, max_sup_price)
        self.assertGreaterEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MIN_PROFIT
        )
        self.assertLessEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MAX_PROFIT
        )
        # self.assertEqual(float(round(analyzer.final_price, 2)), conf["final_price"])

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 941_433.93},
                {
                    "po": {"qty": 500, "price": 730_000},
                    "sup": [
                        {"price": 800_000, "stock": 300},
                        {"price": 700_000, "stock": 200},
                    ],
                },
            )
        ]
    )
    @pytest.mark.skip(reason="Not ready")
    def test_one_po_history_has_price_between_multiple_candidate_suppliers(
        self, conf, param
    ):
        ...

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 0},
                {
                    "po": [
                        {"qty": 10, "price": 730_000},
                        {"qty": 900, "price": 730_000},
                    ],
                    "sup": {"price": 730_000, "stock": 500},
                },
            )
        ]
    )
    @pytest.mark.skip(reason="Not ready")
    def test_multiple_po_histories_and_one_candidate_supplier_has_same_price(
        self, conf, param
    ):
        ...

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 0},
                {
                    "po": [
                        {"qty": 10, "price": 810_000},
                        {"qty": 500, "price": 740_000},
                    ],
                    "sup": {"price": 730_000, "stock": 500},
                },
            )
        ]
    )
    @pytest.mark.skip(reason="Not ready")
    def test_multiple_po_histories_has_higher_price_than_one_candidate_supplier(
        self, conf, param
    ):
        ...

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 0},
                {
                    "po": [
                        {"qty": 10, "price": 720_000},
                        {"qty": 500, "price": 600_000},
                    ],
                    "sup": {"price": 750_000, "stock": 500},
                },
            )
        ]
    )
    @pytest.mark.skip(reason="Not ready")
    def test_multiple_po_histories_has_lower_price_than_one_candidate_supplier(
        self, conf, param
    ):
        ...

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 0},
                {
                    "po": [
                        {"qty": 10, "price": 600_000},
                        {"qty": 500, "price": 600_000},
                    ],
                    "sup": {"price": 750_000, "stock": 500},
                },
            )
        ]
    )
    def test_multiple_po_histories_has_lower_price_than_one_candidate_supplier(
        self, conf, param
    ):
        rfq = RFQFactory(
            customer=self.customer, product=self.product, quantity=conf["rfq_qty"]
        )
        for po in param["po"]:
            POFactory(
                customer=self.customer,
                product=self.product,
                quantity=po["qty"],
                price=po["price"],
            )
        supplier = SupplierFactory()
        SupplierPriceFactory(
            supplier=supplier,
            product=self.product,
            price=param["sup"]["price"],
            available_stock=param["sup"]["stock"],
        )

        analyzer = RFQAnalyzer(rfq).handle()

        self.assertEqual(analyzer.chosen_price, param["sup"]["price"])
        self.assertGreaterEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MIN_PROFIT
        )
        self.assertLessEqual(
            float(round(analyzer.profit_margin, 2)), RFQAnalyzer.MAX_PROFIT
        )

    @parameterized.expand(
        [
            (
                {"rfq_qty": 500, "final_price": 0},
                {
                    "po": [
                        {"qty": 10, "price": 800_000},
                        {"qty": 500, "price": 600_000},
                    ],
                    "sup": {"price": 750_000, "stock": 500},
                },
            )
        ]
    )
    @pytest.mark.skip(reason="Not ready")
    def test_multiple_po_histories_has_price_around_one_candidate_supplier(
        self, conf, param
    ):
        ...
