from string import ascii_letters
from random import choices
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, User
from django.db.models import Model
from django.test import TestCase
from django.urls import reverse
from seobject import kwargs

from .utils import add_two_numbers

from .models import Product, Order

# Create your tests here.
class AddTwoNumbersTestCase(TestCase):

    def test_add_two_numbers(self):
        result = add_two_numbers(2,3)
        self.assertEqual(result, 5)

class ProductCreateViewTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user(username="test_user", password="password12356!!")
        permission = Permission.objects.get(codename="add_product")
        user.user_permissions.add(permission)
        user = User.objects.get(pk=user.pk)
        self.client.force_login(user)

        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
        reverse("shopapp:create_product"),
            {
                "name": self.product_name,
                "description": "test",
                "price": "20000",
                "discount": "10"
            }
        )

        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="test_user", password="password12356!!")
        cls.product = Product.objects.create(name="Best Product", created_by=cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(reverse("shopapp:product_details", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 200)

    def test_product_and_check_content(self):
        response = self.client.get(reverse("shopapp:product_details", kwargs={"pk": self.product.pk}))
        self.assertContains(response, self.product.name)

class ProductListViewTestCase(TestCase):
    fixtures = ["products_fixture.json"]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))

        self.assertQuerySetEqual(qs=Product.objects.filter(archived=False).all(), values=[p.pk for p in response.context["products"]], transform=lambda p: p.pk)

        self.assertTemplateUsed(response, "shopapp/products-list.html")

class OrdersTestViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        User = get_user_model()
        cls.credentials = dict(username="test_user", password="password12356!!")
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

class ProductsDataExportViewTestCase(TestCase):

    fixtures = [
        "products_fixture.json"
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products-export"))
        self.assertEqual(response.status_code, 200)

        products = Product.objects.order_by("pk").all()

        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]

        products_data = response.json()
        self.assertEqual(products_data["products"], expected_data)

class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        User = get_user_model()
        cls.permission = Permission.objects.get(codename="view_order")
        cls.credentials = dict(username="test_user", password="password12356!!")
        cls.user = User.objects.create_user(**cls.credentials)
        cls.user.user_permissions.add(cls.permission)

    def setUp(self) -> None:
        self.client.login(**self.credentials)
        self.order = Order.objects.create(delivery_address="Test_address", promocode="TestPromo", user_id=self.user.pk)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(reverse("shopapp:order_details", kwargs={"pk": self.order.pk}))
        self.assertEqual(response.context["order"].delivery_address, "Test_address")
        self.assertEqual(response.context["order"].promocode, "TestPromo")
        self.assertEqual(response.context["order"].pk, self.order.pk)

class OrderDataExportViewTestCase(TestCase):

    fixtures = [
        "users_fixture.json",
        "orders_fixture.json",
        "products_fixture.json"
    ]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        User = get_user_model()
        cls.credentials = dict(username="test_user", password="password12356!!", is_staff=True)
        cls.user = User.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_get_orders_view(self):
        response = self.client.get(reverse("shopapp:orders-export"))
        self.assertEqual(response.status_code, 200)

        orders = Order.objects.order_by("pk").prefetch_related("products").all()

        expected_data = [
            {
                "pk": order.pk,
                "user": order.user_id,
                "products": list(order.products.values_list('id', flat=True)),
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "created_at": order.created_at.isoformat(),
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(orders_data["orders"], expected_data)