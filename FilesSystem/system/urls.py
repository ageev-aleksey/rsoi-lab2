from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path("test/", views.file_form_upload)
]
