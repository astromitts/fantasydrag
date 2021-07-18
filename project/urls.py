from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from fantasydrag.api.urls import urlpatterns as api_urls
from fantasydrag.urls import urlpatterns as app_urls
from legal.views import PolicyLanding, PrivacyPolicy, EULA

urlpatterns = [
    path('summernote/', include('django_summernote.urls')),
    path('admin/', admin.site.urls),
    path(
        'privacy-policy/',
        PrivacyPolicy.as_view(),
        name='privacy_policy'
    ),
    path(
        'end-user-license-agreement/',
        EULA.as_view(),
        name='eula'
    ),
    path(
        'end-user-license-agreement/',
        TemplateView.as_view(template_name='pages/legal/v1/eula.html'),
        name='eula'
    ),
    path(
        'policy-update/',
        PolicyLanding.as_view(),
        name='policy_update'
    ),
] + app_urls + api_urls
