from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


def product_preview_file_path(instance: "Product", filename: str):
    return f"products/product{instance.pk}/preview/{filename}"

class Product(models.Model):

    class Meta:
        ordering = ["name", "price"]

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_file_path)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='product',
    )

    @property
    def description_short(self) -> str:

        if len(self.description) < 48:
            return self.description
        return self.description[:48] + "..."

    def __str__(self) -> str:
        return f"Product(pk={self.pk}, name={self.name!r})"

    def get_absolute_url(self):
        return reverse('shopapp:product_details', kwargs={"pk": self.pk})

def product_images_directory_path(instance: "ProductImage", filename: str):
    return f"products/product_{instance.product.pk}/preview/{filename}"

class ProductImage(models.Model):


    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=255, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    delivery_address = models.CharField(max_length=100)
    promocode = models.TextField(null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    receipt = models.FileField(null=True, blank=True, upload_to="orders/receipts/")

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")