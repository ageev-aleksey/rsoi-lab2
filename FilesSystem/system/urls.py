from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path("test/", views.file_form_upload),
    path("file/add/", views.file_add),
    path("file/<str:file_uuid>/", views.get_file),
    path("file/<str:file_uuid>/info/", views.get_file_info)
]
