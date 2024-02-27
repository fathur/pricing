import csv
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils import timezone

from bababos.pricing.models import Customer, Logistic, Product, Region, Supplier
from bababos.pricing.services import SupplierRecommender


class Command(BaseCommand):
    help = "Decide the prices"

    def handle(self, *args, **options):
        recommender = SupplierRecommender()
        recommender.handle()
