from django.urls import path

from .views import (
    BashoDetailView,
    BashoListView,
    DivisionDetailView,
    DivisionListView,
    IndexView,
    RikishiDetailView,
    RikishiListView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("rikishi/", RikishiListView.as_view(), name="rikishi-list"),
    path(
        "rikishi/<int:pk>/",
        RikishiDetailView.as_view(),
        name="rikishi-detail",
    ),
    path("division/", DivisionListView.as_view(), name="division-list"),
    path(
        "division/<slug:slug>",
        DivisionDetailView.as_view(),
        name="division-detail",
    ),
    path("basho/", BashoListView.as_view(), name="basho-list"),
    path(
        "basho/<slug:slug>",
        BashoDetailView.as_view(),
        name="basho-detail",
    ),
]
