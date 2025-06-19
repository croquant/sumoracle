from django.views.generic import DetailView, ListView

from ..models import Basho


class BashoListView(ListView):
    """List all basho ordered by most recent."""

    model = Basho
    template_name = "basho_list.html"
    ordering = ["-year", "-month"]


class BashoDetailView(DetailView):
    """Display details for a single basho."""

    model = Basho
    template_name = "basho_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "basho"
