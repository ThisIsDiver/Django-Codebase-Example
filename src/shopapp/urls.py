from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter
from .views import (
    ShopIndexView,
    GroupsListView,
    ProductsListView,
    OrdersListView,
    ProductCreateView,
    OrderCreateView,
    ProductDetailsView,
    OrderDetailView,
    ProductUpdateView,
    ProductDeleteView,
    OrderUpdateView,
    OrderDeleteView,
    ProductsDataExportView,
    OrdersDataExportView,
    UserOrdersListView,
    UserOrdersExportView
)

from .api import (
    ProductViewSet,
    OrderViewSet,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("api/", include(routers.urls)),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("products/create/", ProductCreateView.as_view(), name="create_product"),
    path("products/update/<int:pk>/", ProductUpdateView.as_view(), name="update_product"),
    path("products/delete/<int:pk>/", ProductDeleteView.as_view(), name="delete_product"),
    path("orders/create/", OrderCreateView.as_view(), name="create_order"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("orders/update/<int:pk>/", OrderUpdateView.as_view(), name="update_order"),
    path("orders/delete/<int:pk>/", OrderDeleteView.as_view(), name="delete_order"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path("orders/export/", OrdersDataExportView.as_view(), name="orders-export"),
    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user-orders"),
    path("users/<int:user_id>/orders/export/", UserOrdersExportView.as_view(), name="user-orders-export")
]
