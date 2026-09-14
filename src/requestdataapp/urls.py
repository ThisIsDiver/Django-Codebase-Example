from django.urls import path
from .views import process_get_query, user_form, handle_file_upload

app_name = "requestsdataapp"

urlpatterns = [
    path("get/", process_get_query, name="get-view"),
    path("bio/", user_form, name="user-form"),
    path("upload/", handle_file_upload, name="upload-file")
]
