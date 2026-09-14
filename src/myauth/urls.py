from django.contrib.auth.views import LoginView
from django.urls import path, include
from .views import (
    get_cookie_view,
    set_cookie_view,
    get_session_view,
    set_session_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    UpdateProfileView,
    UserListView,
    UserDetailView,
    HelloView
)

app_name = "myauth"

urlpatterns = [
    path("login/", LoginView.as_view(
        template_name="myauth/login.html",
        redirect_authenticated_user=True
        ),
        name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("cookie/get/", get_cookie_view, name="get-cookie"),
    path("cookie/set/", set_cookie_view, name='set-cookie'),
    path("session/set/", set_session_view, name='set-session'),
    path("session/get/", get_session_view, name='get-session'),
    path("about-me/", AboutMeView.as_view(), name='about-me'),
    path("register/", RegisterView.as_view(), name='register'),
    path("update/", UpdateProfileView.as_view(), name='update'),
    path("update/<int:pk>/", UpdateProfileView.as_view(), name='update-user'),
    path("", UserListView.as_view(), name="user-list"),
    path("about/<int:pk>/", UserDetailView.as_view(), name="user-about"),
    path("hello/", HelloView.as_view(), name="Hello-world")
]
