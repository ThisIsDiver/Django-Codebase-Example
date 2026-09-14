from urllib import response
from random import random
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView
from django.contrib.auth.models import User
from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, View
from django.views.generic.detail import DetailView
from django.utils.translation import gettext_lazy as _, ngettext_lazy
from django.views.decorators.cache import cache_page
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from .models import Profile
from .forms import MyAuthProfileForm, AvatarForm

class HelloView(View):
    hello_message = _("welcome hello world")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = self.request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext_lazy(
            "one product",
            "{count} products",
            items
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.hello_message}</h1>"
            f"<h2>{products_line}</h2>"
        )


class AboutMeView(UpdateView):
    model = Profile
    fields = ("avatar",)
    template_name = "myauth/about-me.html"
    success_url = reverse_lazy("myauth:about-me")

    def get_object(self):
        return self.request.user.profile

class RegisterView(CreateView):
    template_name = "myauth/register.html"
    form_class = MyAuthProfileForm
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        avatar_file = form.cleaned_data.get("avatar")
        Profile.objects.create(user=self.object, avatar=avatar_file)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        login(request=self.request, user=user)

        return response

class UpdateProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = AvatarForm
    template_name = "myauth/update.html"

    def test_func(self):
        user = self.request.user
        profile = self.get_object()

        if user.is_superuser:
            return True

        return user.is_staff or profile.user == user

    def get_success_url(self) -> str:
        profile_pk = self.kwargs.get("pk")
        if profile_pk:
            return reverse("myauth:user-about", kwargs={"pk": profile_pk})
        return reverse("myauth:about-me")


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("auth:login"))

class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")

def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie get")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

@cache_page(60)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")

@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spamggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default value")
    return HttpResponse(f"SESSION: {value!r}")

class UserListView(ListView):
    model = Profile
    template_name = "myauth/user-list.html"
    context_object_name = "profiles"

class UserDetailView(DetailView):
    model = Profile
    template_name = "myauth/about-user.html"
    context_object_name = "profile_user"