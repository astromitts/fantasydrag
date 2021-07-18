from django.contrib import admin
from django.urls import path

from fantasydrag.api.urls import urlpatterns as api_urls
from fantasydrag.urls import urlpatterns as app_urls

urlpatterns = [
    path('admin/', admin.site.urls),
] + app_urls + api_urls
