from django.urls import path, include
from . import views
urlpatterns = [
    path("questions/", views.get_questions_page)
]