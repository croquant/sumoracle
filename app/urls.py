from django.urls import path

from .views import (
    BashoDetailView,
    BashoListView,
    DivisionDetailView,
    DivisionListView,
    IndexView,
    RikishiDetailView,
    RikishiHistoryView,
    RikishiListView,
    RikishiRatingView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("rikishi/", RikishiListView.as_view(), name="rikishi-list"),
    path(
        "rikishi/<int:pk>/",
        RikishiDetailView.as_view(),
        name="rikishi-detail",
    ),
    path(
        "rikishi/<int:pk>/history/",
        RikishiHistoryView.as_view(),
        name="rikishi-history",
    ),
    path(
        "rikishi/<int:pk>/ratings/",
        RikishiRatingView.as_view(),
        name="rikishi-ratings",
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
