from django.urls import path

from .views import DivisionDetailView, DivisionListView, IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("division/", DivisionListView.as_view(), name="division-list"),
    path(
        "division/<slug:slug>",
        DivisionDetailView.as_view(),
        name="division-detail",
    ),
]
