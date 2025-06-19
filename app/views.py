from django.views.generic import DetailView, ListView, TemplateView

from .models import Division, Rikishi


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


class RikishiListView(ListView):
    model = Rikishi
    template_name = "rikishi_list.html"
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get("active") is not None:
            queryset = queryset.filter(intai__isnull=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active = self.request.GET.get("active") is not None
        context["active_only"] = active
        base = self.request.path
        context["toggle_url"] = base if active else f"{base}?active=1"
        return context


class RikishiDetailView(DetailView):
    model = Rikishi
    template_name = "rikishi_detail.html"
    slug_field = "id"
    slug_url_kwarg = "pk"
    context_object_name = "rikishi"
