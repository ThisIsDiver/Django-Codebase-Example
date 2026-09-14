from django.contrib.auth.models import User

from django.core.management import BaseCommand
from django.db.models.aggregates import Avg, Min, Max, Count, Sum

from shopapp.models import Product, Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo aggregate")


        # result = Product.objects.filter(name__contains="Smart").aggregate(
        #     Avg("price"),
        #     Max("price"),
        #     Min("price"),
        #     min_price=Min("price"),
        #     count=Count("id"),
        # )
        # print(result)

        orders = Order.objects.annotate(
            total=Sum("products__price", default=0),
            products_count=Count("products")
        )
        for order in orders:
            print(f"{order} #{order.id} "
                  f"with {order.products_count} "
                  f"products worth {order.total}"
                  )

        self.stdout.write(self.style.SUCCESS(f"Done"))
