rom django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('answers/add', views.add_answer),
    path('answers/<str:uuid>', views.get_or_del_answer),
]
