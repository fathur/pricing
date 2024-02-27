from django.db import models

from bababos.utilities.utils import Model


class Transaction(Model):
    class Meta:
        db_table = "transactions"
        unique_together = ("rfq", "supplier_price")

    rfq = models.ForeignKey(
        to="pricing.RFQ", on_delete=models.CASCADE, related_name="transactions"
    )
    status = models.CharField(default="pending", max_length=100)
    supplier_price = models.ForeignKey(
        to="pricing.SupplierPrice", on_delete=models.CASCADE
    )
    chosen_price = models.DecimalField(max_digits=21, decimal_places=5)
    final_price = models.DecimalField(max_digits=21, decimal_places=5)
    analyzed_profit_margin = models.DecimalField(max_digits=8, decimal_places=5)
    quantity = models.PositiveIntegerField()
    note = models.TextField(null=True, blank=True)

    @property
    def profit(self):
        return self.final_price - self.chosen_price
