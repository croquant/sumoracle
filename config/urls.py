from django.contrib import admin
from django.urls import include, path

import app.api

urlpatterns = [
    path("", include("app.urls")),
    path("admin/", admin.site.urls),
    path("api/", app.api.api.urls),
]
