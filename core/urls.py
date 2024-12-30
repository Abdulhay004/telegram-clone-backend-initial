from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.contrib.auth.decorators import user_passes_test
from debug_toolbar.toolbar import debug_toolbar_urls

def is_superuser(user):
    return True


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(
        [   # local apps
            path('users/', include('user.urls')),
            # another apps
            path('schema/', user_passes_test(is_superuser)(SpectacularAPIView.as_view()), name='schema'),
            path('swagger/', user_passes_test(is_superuser)(SpectacularSwaggerView.as_view()), name='swagger-ui'),
            path('redoc/', user_passes_test(is_superuser)(SpectacularRedocView.as_view()), name='redoc'),
            ]))

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()
