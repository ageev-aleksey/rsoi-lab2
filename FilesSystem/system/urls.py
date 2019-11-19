from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path("test/", views.file_form_upload),
    path("files/add/", views.file_add),
    path("files/all/", views.get_all_files),
    path("files/list/", views.get_list_of_files_info),
    path("files/<str:file_uuid>/", views.file_work),
    path("files/<str:file_uuid>/info/", views.get_file_info),

]
