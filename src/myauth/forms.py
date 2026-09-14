from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class MyAuthProfileForm(UserCreationForm):
    avatar = forms.ImageField(
        required=False,
        label="Avatar",
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": "image/*"
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"})
        }