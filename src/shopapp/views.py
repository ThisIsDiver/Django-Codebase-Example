from timeit import default_timer
from typing import Any

from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.db.models import QuerySet
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from .models import Product, Order, ProductImage
from .forms import ProductForm, OrderForm, GroupForm
from .serializers import OrderSerializer


class ShopIndexView(View):
    # @method_decorator(cache_page(60))
    def get(self, request: HttpRequest):
        products = [("Laptop", 1000), ("PC", 10999), ("tablet", 3222)]
        context = {"time_running": default_timer(), "products": products}

        return render(request, "shopapp/shop-index.html", context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest):
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, "shopapp/groups-list.html", context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)

class ProductDetailsView(DetailView):
    template_name = "shopapp/product-details.html"
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"

class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    model = Product
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(archived=False)

class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )
    context_object_name = "orders"

class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )
    context_object_name = "order"

class ProductCreateView(PermissionRequiredMixin, CreateView):
    def test_func(self):
        return self.request.user.is_superuser

    permission_required = "shopapp.add_product"
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.request.method in ["POST", "PUT"]:
            kwargs["files"] = self.request.FILES

        return kwargs


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    permission_required = "shopapp.change_product"
    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"
    raise_exception = True

    def test_func(self):
        product = self.get_object()
        user = self.request.user

        if user.is_superuser:
            return True

        is_author = (user == product.created_by)
        has_change_permission = user.has_perm("shopapp.change_product")

        return is_author and has_change_permission

    def get_success_url(self) -> str:
        return reverse_lazy("shopapp:product_details", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.request.method in ["POST", "PUT"]:
            kwargs["files"] = self.request.FILES

        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        images = self.request.FILES.getlist("images")

        for image in images:
            ProductImage.objects.create(product=self.object, image=image)

        return response

class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "shopapp.delete_product"
    model = Product
    fields = "name", "description", "price", "discount"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("shopapp:orders_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['products'].queryset = form.fields['products'].queryset.filter(archived=False)
        return form

class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name_suffix = "_update_form"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['products'].queryset = form.fields['products'].queryset.filter(archived=False)
        return form

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk}
        )

class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")

class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]

            cache.get(cache_key, products_data, 5*60)

        return JsonResponse({"products": products_data})

class OrdersDataExportView(View):

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by(
            "pk"
        ).prefetch_related("products")
        orders_data = [
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
        print(orders_data)
        return JsonResponse({"orders": orders_data})

class LatestProductFeed(Feed):
    title = "Products (latest)"
    description = "Updates on changes or additions new products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return Product.objects.filter(pub_date__isnull=False).order_by("-pub_date")[:5]

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item:Product):
        return item.description[:200]


class UserOrdersListView(ListView):
    template_name = "shopapp/user_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return Order.objects.filter(user_id=user_id).select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders = context["orders"]

        if orders.exists():
            context["selected_user"] = orders.first().user
        else:
            context["selected_user"] = get_object_or_404(User, pk=self.kwargs.get("user_id"))


        return context

class UserOrdersExportView(View):
    def get(self, request: HttpRequest, **kwargs) -> JsonResponse:
        user_id = self.kwargs.get("user_id")

        cache_key = f"orders-export-cache-{user_id}"
        orders_data = cache.get(cache_key)
        if orders_data is None:
            orders = Order.objects.order_by(
                "pk"
            ).filter(user_id=user_id).prefetch_related("products").order_by("pk")

            serializer = OrderSerializer(orders, many=True)

            orders_data = serializer.data

            cache.set(cache_key, orders_data, 30)

        return JsonResponse({"orders": orders_data})

