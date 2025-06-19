from django.urls import path

from .views import (
    DivisionDetailView,
    DivisionListView,
    IndexView,
    RikishiListView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("rikishi/", RikishiListView.as_view(), name="rikishi-list"),
    path("division/", DivisionListView.as_view(), name="division-list"),
    path(
        "division/<slug:slug>",
        DivisionDetailView.as_view(),
        name="division-detail",
    ),
]
