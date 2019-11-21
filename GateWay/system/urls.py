from django.urls import path, include

from . import views
urlpatterns = [
    path("questions/", views.get_questions_page),
    path("questions/add/", views.create_question),
    path("questions/<str:question_uuid>/", views.get_question),
    path("questions/<str:question_uuid>/answers/add/", views.create_answer),
    path("questions/<str:quuid>/files/", views.attach_file_question),
    path("questions/<str:quuid>/answers/<str:auuid>/files/", views.attach_file_answer),
    path("files/<str:fuuid>/", views.download_file_controller),
    path("files/", views.delete_file_controller),
    path("questions/<str:question_uuid>/answers/", views.delete_answers),
]