from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from shopapp.models import Order, Product


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")
        user = User.objects.get(username="admin")
        products: Sequence[Product] = Product.objects.only("pk", "name").all()
        order, created = Order.objects.get_or_create(
            delivery_address="Улица Кулешова 25", promocode="prom3o", user=user
        )

        for product in products:
            order.products.add(product)

        order.save()

        self.stdout.write(self.style.SUCCESS(f"Order created - {user} - {order}"))
