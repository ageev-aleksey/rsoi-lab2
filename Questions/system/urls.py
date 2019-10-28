from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('questions/all/<int:page>/', views.get_questions),
    path('questions/id/<str:uuid>/', views.get_question_detail_and_answers),

]
