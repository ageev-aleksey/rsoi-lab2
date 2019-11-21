from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('api/v1/questions/add/', views.add_question),
    path('api/v1/questions/', views.get_questions),
    path('api/v1/questions/<str:uuid>/', views.question),
    path('api/v1/questions/<str:quuid>/files/<str:fuuid>/', views.attach_file),
    path('api/v1/questions/<str:quuid>/exist/', views.is_exist),
    path("api/v1/files/<str:fuuid>/", views.try_delete)
]
