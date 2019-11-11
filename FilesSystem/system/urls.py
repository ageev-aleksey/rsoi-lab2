from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path("test/", views.file_form_upload),
    path("api/v1/file/add", views.file_add),
    path("api/v1/file/<str:file_name>", views.get_file)
]
