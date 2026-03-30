from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("users/", include("users.urls")),
    path("store/", include("store.urls")),
]

handler404 = "core.views.custom_404"

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
