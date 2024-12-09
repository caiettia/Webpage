from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio, name='portfolio'),
    path('tag/<str:tag_name>/', views.projects_by_tag, name='projects_by_tag'),
]