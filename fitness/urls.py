
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/activities/', include('activities.urls')),
    path('', TemplateView.as_view(template_name='activities/home.html'), name='home'),
    path('', include('activities.urls_web')),
    path('auth/', include('users.urls_web')),
]
