from django.contrib.auth.models import Group
from django import forms
from django.core import validators

from shopapp.models import Product, Order

class MultiFileInput(forms.FileInput):
    allow_multiple_selected = True
    def value_from_datadict(self, data, files, name):
        return files.getlist(name)

class MultiFileField(forms.FileField):
    widget = MultiFileInput
    def clean(self, data, initial=None):
        return [super().clean(f) for f in data] if data else []

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    images = MultiFileField(required=False)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "user", "products", "delivery_address", "promocode"
        labels = {
            "user": "Пользователь",
            "products": "Продукт",
            "delivery_address": "Адрес доставки",
            "promocode": "Промокод",
        }
        widgets = {
            "delivery_address": forms.Textarea(
                attrs={
                    "class": "form-control custom-title",
                    "placeholder": "Введите адрес",
                    "rows": 3,
                }
            ),
            "promocode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите промокод"}
            ),
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "name",

class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
