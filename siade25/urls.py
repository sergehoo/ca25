"""
URL configuration for siade25 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from administration.views import scan_qr_code
from public.views import HomePageView, blog_list, blog_detail, soumettre_temoignage

urlpatterns = [
    path("api/", include('administration.api.urls')),  # API indépendante
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Inclure toutes les URLs d'authentification
    path('i18n/', include('django.conf.urls.i18n')),
    path('organisator/', include('administration.urls')),
    path('blog/', blog_list, name="blog_list"),
    path('blog/<slug:slug>/', blog_detail, name="blog_detail"),
    path('soumettre-temoignage/', soumettre_temoignage, name="soumettre_temoignage"),

    path('', HomePageView.as_view(), name='home'),

    path("sessions/scan/<slug:slug>/", scan_qr_code, name="scan-qr"),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

