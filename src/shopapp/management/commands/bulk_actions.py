from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    help = "Create products in bulk"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            default="admin",
            help="Username of the product creator",
        )

    def handle(self, *args, **options):
        self.stdout.write("Create products bulk actions")
        user = User.objects.get(username=options["user"])

        result = Product.objects.filter(
            name__contains="Smart"
        ).update(discount=10)

        print(result)

        # info = [
        #     ("Smart", 888),
        #     ("TV", 999),
        #     ("TESTPC", 39334),
        # ]
        #
        # products = [
        #     Product(name=name, price=price, created_by=user)
        #     for name, price in info
        # ]
        #
        # result = Product.objects.bulk_create(products)
        #
        # for obj in result:
        #     self.stdout.write(str(obj))

        self.stdout.write(self.style.SUCCESS("Done"))