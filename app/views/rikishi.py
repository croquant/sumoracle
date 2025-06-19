from django.db.models import Q
from django.views.generic import DetailView, ListView

from ..models import Heya, Rank, Rikishi


class RikishiListView(ListView):
    model = Rikishi
    template_name = "rikishi_list.html"
    paginate_by = 50
    partial_template_name = "partials/rikishi_rows.html"

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return [self.partial_template_name]
        return [self.template_name]

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.GET
        if params.get("active") is not None:
            queryset = queryset.filter(intai__isnull=True)
        if q := params.get("q"):
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(name_jp__icontains=q)
            )
        if heya := params.get("heya"):
            queryset = queryset.filter(heya__slug=heya)
        if rank := params.get("rank"):
            queryset = queryset.filter(rank__slug=rank)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        active = params.get("active") is not None
        context["active_only"] = active
        base = self.request.path
        context["toggle_url"] = base if active else f"{base}?active=1"

        context["heyas"] = Heya.objects.all()
        context["ranks"] = Rank.objects.all()
        context["query"] = params.get("q", "")
        context["selected_heya"] = params.get("heya", "")
        context["selected_rank"] = params.get("rank", "")

        params.pop("page", None)
        query_string = params.urlencode()
        context["query_params"] = f"&{query_string}" if query_string else ""
        return context


class RikishiDetailView(DetailView):
    model = Rikishi
    template_name = "rikishi_detail.html"
    slug_field = "id"
    slug_url_kwarg = "pk"
    context_object_name = "rikishi"
