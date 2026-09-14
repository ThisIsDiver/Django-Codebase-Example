from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding, user):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )

    reader = DictReader(csv_file)

    products = list()

    for row in reader:
        products.append(Product(**row))
        Product.objects.create(
            name=row["name"],
            description=row["description"],
            price=row["price"],
            discount=row["discount"],
            created_by=user
        )

    return products

def save_csv_orders(file, encoding, user):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )

    reader = DictReader(csv_file)

    orders = list()

    for row in reader:
        order = Order.objects.create(
            delivery_address=row["delivery_address"],
            promocode=row["promocode"],
            user_id=row["user_id"],
            receipt=row["receipt"]
        )

        order.products.set(row["products"].split(","))

        orders.append(order)

    return orders
