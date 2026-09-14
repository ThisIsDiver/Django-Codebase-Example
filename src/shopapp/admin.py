from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products, save_csv_orders
from .models import Product, Order, ProductImage
from .forms import CSVImportForm
from .admin_mixins import ExportAsCSVMixin


@admin.action(description="Archive products")
def mark_archived(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def unmark_archived(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(archived=False)


class OrderInline(admin.TabularInline):

    model = Product.orders.through


class ProductImageInline(admin.StackedInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"

    actions = [
        mark_archived,
        unmark_archived,
        "export_as_csv",
    ]

    inlines = [
        OrderInline,
        ProductImageInline
    ]

    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"

    ordering = "name", "pk"

    """
    Ниже самое простое решение в рамках задания на поиск с числовым и строковым полем.
    В уроках фигурировал вторым полем description. Я заменил его на pk
    """

    search_fields = "pk", "name"

    fieldsets = [
        (
            None,
            {
                "fields": ("name", "description"),
            },
        ),
        (
            "Price options",
            {
                "fields": ("price", "discount"),
                "classes": ("collapse", "wide"),
            },
        ),
        (
            "Images",
            {
                "fields": ("preview",),
            },
        ),
        (
            "Extra options",
            {
                "fields": ("archived",),
                "classes": ("collapse",),
                "description": "Extra Options. Field 'archived' is for soft delete",
            },
        ),
    ]

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form
            }

            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form
            }
            return render(request, "admin/csv_form.html", context, status=400)

        csv_file = save_csv_products(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
            user=request.user
        )

        self.message_user(request, "Data from CSV was imported")

        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import_products_csv/", self.import_csv, name="import-products-csv")
        ]
        return new_urls + urls


class ProductInline(admin.StackedInline):
    model = Order.products.through

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/orders_changelist.html"

    inlines = [
        ProductInline,
    ]

    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order):
        return obj.user.first_name or obj.user.username



    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form
            }

            return render(request, "admin/csv_form.html", context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form
            }
            return render(request, "admin/csv_form.html", context, status=400)

        csv_file = save_csv_orders(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
            user=request.user
        )

        self.message_user(request, "Data from CSV was imported")

        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import_orders_csv/", self.import_csv, name="import-orders-csv")
        ]
        return new_urls + urls


