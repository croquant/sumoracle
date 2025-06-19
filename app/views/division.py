from django.http import Http404
from django.views.generic import DetailView, ListView

from ..models import Division


class DivisionListView(ListView):
    model = Division
    template_name = "division_list.html"


class DivisionDetailView(DetailView):
    model = Division
    template_name = "division_detail.html"
    slug_field = "name"
    slug_url_kwarg = "slug"
    context_object_name = "division"

    def get_object(self, queryset=None):
        """Return the division matching the URL slug case-insensitively."""
        queryset = queryset or self.get_queryset()
        slug = self.kwargs.get(self.slug_url_kwarg)
        if slug is None:
            raise Http404("No division specified")
        try:
            return queryset.get(name__iexact=slug)
        except Division.DoesNotExist as exc:
            raise Http404("Division not found") from exc
