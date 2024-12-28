"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import to include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf.urls.static import static
from authapp.views import redirect_authenticated_user_view

urlpatterns = i18n_patterns(
    path('auth/', include(('authapp.urls', 'authapp'), namespace='auth')),
    path('admin/', include(('adminapp.urls', 'adminapp'), namespace='admin')),
    path('vendor/', include(('vendorapp.urls', 'vendorapp'), namespace='vendor')),
    path('customer/', include(('customerapp.urls', 'customerapp'), namespace='customer')),
    path('tz_detect/', include('tz_detect.urls')),
    path('rosetta/', include('rosetta.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += (path('', redirect_authenticated_user_view, name='redirect_authenticated_user_view'),)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler400 = 'authapp.views.entry_bad_request'
handler403 = 'authapp.views.entry_forbidden'
handler404 = 'authapp.views.entry_not_found'
# handler500 = 'authapp.views.entry_internal_server_error'
