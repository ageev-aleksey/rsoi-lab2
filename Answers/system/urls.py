from django.urls import path
from . import views
urlpatterns = [
    path('answers/add/', views.add_answer),
    path('answers/add/test/', views.add_answer_test),
    path('answers/', views.get_answers_page),
    path('answers/count', views.count_answers),
    path('answers/counts', views.count_answers_for_list_questions),
    path('answers/<str:auuid>/exist/', views.is_exist),
    path('answers/<str:uuid>/', views.get_or_del_answer),
    path('answers/<str:auuid>/files/<str:fuuid>/', views.attach_file),
]
