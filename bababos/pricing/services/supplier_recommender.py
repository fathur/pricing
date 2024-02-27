import decimal
from typing import List

import django.db.utils
from django.db.models import Prefetch

from bababos.pricing.models import PO, RFQ, Supplier, Transaction, SupplierPrice
from bababos.utilities.utils import Collection


class CandidateSupplierPrice:
    supplier_price: SupplierPrice
    available_stock: int
    purchased_stock: int
    remaining_stock: int
    price: float
    total: float

    def __init__(self, **kwargs):
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"<bababos...{class_name}: ({self.supplier_price.id})>"


class RFQAnalyzer:

    MIN_PROFIT = 10 / 100
    MAX_PROFIT = 50 / 100

    # for simplicity,
    # this number will same across product and supplier
    MIN_AMOUNT_FOR_MAX_PROFIT = 1
    MAX_AMOUNT_FOR_MIN_PROFIT = 100

    def __init__(self, rfq: RFQ):
        self.rfq = rfq
        self.customer = rfq.customer
        self.product = rfq.product
        self.quantity = rfq.quantity

        self.profit_margin: decimal.Decimal | None = None
        self.chosen_price: decimal.Decimal | None = None
        self.final_price: decimal.Decimal | None = None
        self.supplier_prices = []
        self.note: str | None = None

    def handle(self):

        self.set_profit_margin(self.rfq.quantity)

        po_histories = self.get_po_histories()
        self.get_candidate_suppliers()

        if len(po_histories) == 1:

            past_po = po_histories[0]

            if len(self.supplier_prices) == 1:
                supplier_price = self.supplier_prices[0]
                if past_po.price <= supplier_price.price:
                    self._set_common_pricing(supplier_price.price)
                    self.set_note(
                        "Single PO history, single supplier price, and last PO history price less than or equal with candidate supplier price"
                    )

                elif past_po.price > supplier_price.price:
                    profit_margin = decimal.Decimal(
                        (past_po.price - supplier_price.price) / supplier_price.price
                    )
                    if profit_margin < self.MIN_PROFIT:
                        profit_margin = decimal.Decimal(self.MIN_PROFIT)
                        self.chosen_price = supplier_price.price
                        self.final_price = self.chosen_price + (
                            self.chosen_price * profit_margin
                        )
                    elif profit_margin > self.MAX_PROFIT:
                        profit_margin = decimal.Decimal(self.MAX_PROFIT)
                        self.chosen_price = supplier_price.price
                        self.final_price = self.chosen_price + (
                            self.chosen_price * profit_margin
                        )
                    else:
                        self.chosen_price = past_po.price
                        self.final_price = past_po.price

                    self.profit_margin = profit_margin
                    self.set_note(
                        "Single PO history, single supplier price, and last PO history price greater than candidate supplier price"
                    )

                else:
                    raise Exception("Something wrong!")

            else:
                higher_bids_than_po_history = []
                unique_bids = []
                for supplier_price in self.supplier_prices:
                    if supplier_price.price not in unique_bids:
                        unique_bids.append(supplier_price.price)
                    if supplier_price.price > past_po.price:
                        higher_bids_than_po_history.append(supplier_price.price)

                if len(higher_bids_than_po_history) >= 1:
                    chosen_price = max(higher_bids_than_po_history)
                    self._set_common_pricing(chosen_price)
                    self.set_note(
                        f"Single PO history, {len(self.supplier_prices)} supplier prices, and has more than one higher supplier price compared with last PO history"
                    )

                else:

                    if len(unique_bids) == 1:
                        unique_bid = unique_bids[0]
                        if unique_bid == past_po.price:
                            self._set_common_pricing(unique_bid)
                            self.set_note(
                                f"Single PO history, {len(self.supplier_prices)} supplier prices, and has one unique supplier price that equal with last PO history"
                            )
                        else:
                            ...

                    else:
                        max_bid = max(unique_bids)

                        profit_margin = decimal.Decimal(
                            (past_po.price - max_bid) / max_bid
                        )
                        if profit_margin < self.MIN_PROFIT:
                            profit_margin = decimal.Decimal(self.MIN_PROFIT)
                            self.chosen_price = past_po.price
                            self.final_price = self.chosen_price + (
                                self.chosen_price * profit_margin
                            )
                        else:
                            self.chosen_price = past_po.price
                            self.final_price = past_po.price

                        self.profit_margin = profit_margin
                        self.set_note(
                            f"Single PO history, {len(self.supplier_prices)} supplier prices, and has multiple unique supplier price"
                        )

        else:
            unique_past_po_prices = []
            for po_history in po_histories:
                if po_history.price not in unique_past_po_prices:
                    unique_past_po_prices.append(po_history.price)

            if len(self.supplier_prices) == 1:
                supplier_price = self.supplier_prices[0]
                if len(unique_past_po_prices) == 1:
                    unique_past_po_price = unique_past_po_prices[0]
                    if supplier_price.price == unique_past_po_price:
                        print("A1.1")
                    elif supplier_price.price > unique_past_po_price:
                        self._set_common_pricing(supplier_price.price)
                        self.set_note(
                            f"Has {len(po_histories)} PO histories but all unique, one supplier price, and supplier price greater than one unique PO history"
                        )
                    else:
                        self._set_common_pricing(supplier_price.price)
                        self.set_note(
                            f"Has {len(po_histories)} PO histories but all unique, one supplier price, and supplier price less than one unique PO history"
                        )
                else:
                    if supplier_price.price < min(unique_past_po_prices):

                        print("A2.1")
                    elif supplier_price.price > max(unique_past_po_prices):
                        self._set_common_pricing(supplier_price.price)
                        self.set_note(
                            f"Has {len(po_histories)} PO histories, one supplier price, and supplier price greater tha max PO histories"
                        )
                    else:
                        self._set_common_pricing(supplier_price.price)
                        self.set_note(
                            f"Has {len(po_histories)} PO histories, one supplier price, and supplier price between PO histories"
                        )

            else:
                # SP: [Decimal("1_261_261.26100"), Decimal("1_447_747.74800")] -> lowest: 1_261_261
                # PO: [Decimal('2_542_785.00000'), Decimal('1_259_831.00000'), Decimal('1_321_171.00000')]
                self._set_common_pricing(min([sp.price for sp in self.supplier_prices]))
                self.set_note(
                    f"Has {len(po_histories)} PO histories, {len(self.supplier_prices)} supplier prices"
                )
        return self

    def _set_common_pricing(self, chosen_price):
        self.final_price = chosen_price + (chosen_price * self.profit_margin)
        self.chosen_price = chosen_price

    def get_candidate_suppliers(self):
        supplier_prices = (
            Collection.of(self.product.supplier_prices.all())
            .filter(product=self.product)
            .order_by("price")
            .get()
        )
        selected_suppliers = []
        leftover = self.quantity
        for supplier_price in supplier_prices:
            available_stock = supplier_price.available_stock
            price = supplier_price.price
            if available_stock > 0 and leftover > 0:
                purchased_stock = (
                    leftover if available_stock >= leftover else available_stock
                )
                leftover = leftover - purchased_stock
                selected_suppliers.append(
                    CandidateSupplierPrice(
                        supplier_price=supplier_price,
                        available_stock=available_stock,
                        purchased_stock=purchased_stock,
                        remaining_stock=(available_stock - purchased_stock),
                        price=price,
                        total=(price * purchased_stock),
                    )
                )

        self.supplier_prices = selected_suppliers
        return self

    def get_po_histories(self):
        return Collection.of(self.customer.POs.all()).filter(product=self.product).get()

    def set_profit_margin(self, quantity):

        if quantity > self.MAX_AMOUNT_FOR_MIN_PROFIT:
            margin = self.MIN_PROFIT * 100
        elif quantity < self.MIN_AMOUNT_FOR_MAX_PROFIT:
            margin = self.MAX_PROFIT * 100
        else:

            margin = (self.MAX_PROFIT * 100) - (
                (quantity - self.MIN_AMOUNT_FOR_MAX_PROFIT)
                * (
                    ((self.MAX_PROFIT * 100) - (self.MIN_PROFIT * 100))
                    / (self.MAX_AMOUNT_FOR_MIN_PROFIT - self.MIN_AMOUNT_FOR_MAX_PROFIT)
                )
            )
        self.profit_margin = decimal.Decimal(margin) / 100

    def set_note(self, note):
        self.note = note
        return self


class SupplierRecommender:
    """
    - Take the lowest price of supplier
    - Buy with more volume cheaper than buy few
    """

    def handle(self):

        # Look at RFQ, where they want to ask for pricing
        request_for_quotations = (
            RFQ.objects.select_related("product", "customer")
            .prefetch_related(
                Prefetch(
                    "customer__POs", queryset=PO.objects.select_related("product")
                ),
                "product__supplier_prices",
            )
            .only(
                "quantity",
                "product__sku",
                "customer__code",
            )
            .iterator(chunk_size=100)
        )

        for rfq in request_for_quotations:
            analyzer = RFQAnalyzer(rfq).handle()
            for supplier in analyzer.supplier_prices:
                try:
                    rfq.transactions.create(
                        supplier_price=supplier.supplier_price,
                        chosen_price=analyzer.chosen_price,
                        final_price=analyzer.final_price,
                        analyzed_profit_margin=analyzer.profit_margin,
                        quantity=supplier.purchased_stock,
                        note=analyzer.note,
                    )
                except django.db.utils.IntegrityError:
                    continue
