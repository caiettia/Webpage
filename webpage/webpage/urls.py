from django.contrib import admin
from django.urls import include, path
from members import views as members_views
from projects import views as projects_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', projects_views.portfolio, name='default'), 
    path('portfolio/', include('projects.urls')),
    path('contact/', include('members.urls')),
    path('home/', projects_views.home, name='home'),
]