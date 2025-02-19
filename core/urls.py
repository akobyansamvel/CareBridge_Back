# core/urls.py

from django.contrib import admin
from django.urls import path, include
from core.routers import router
from authentication.views import UserViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
]