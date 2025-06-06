from django.urls import path

from .views import DivisionDetailView, DivisionListView

urlpatterns = [
    path("division/", DivisionListView.as_view(), name="division-list"),
    path("division/<slug:slug>", DivisionDetailView.as_view(), name="division-detail"),
]
