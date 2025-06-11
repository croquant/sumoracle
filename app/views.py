from django.views.generic import DetailView, ListView, TemplateView

from .models import Division


class IndexView(TemplateView):
    template_name = "index.html"


class DivisionListView(ListView):
    model = Division
    template_name = "division_list.html"


class DivisionDetailView(DetailView):
    model = Division
    template_name = "division_detail.html"
    slug_field = "name"
    slug_url_kwarg = "slug"
    context_object_name = "division"
