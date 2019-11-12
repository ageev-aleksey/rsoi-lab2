from django.urls import path
from . import views
urlpatterns = [
    path('answers/add/', views.add_answer),
    path('answers/add/test/', views.add_answer_test),
    path('answers/', views.get_answers_page),
    path('answers/<str:uuid>/', views.get_or_del_answer),
]
