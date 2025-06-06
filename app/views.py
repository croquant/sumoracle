from django.views.generic import DetailView, ListView

from .models import Division


class DivisionListView(ListView):
    model = Division
    template_name = "division_list.html"


class DivisionDetailView(DetailView):
    model = Division
    template_name = "division_detail.html"
    slug_field = "name"
    slug_url_kwarg = "slug"
    context_object_name = "division"
