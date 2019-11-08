from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('api/v1/questions/add/', views.add_question),
    path('api/v1/questions/<int:page>/', views.get_questions),
    path('api/v1/questions/<str:uuid>/', views.question),
    path('api/v1/questions/<str:uuid>/answers/add/', views.add_answer_to_question),
    path('api/v1/questions/<str:question_uuid>/answers/<str:answer_uuid>/', views.delete_answer)
]
