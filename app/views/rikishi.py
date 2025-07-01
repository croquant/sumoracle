from django.db.models import Q
from django.views.generic import DetailView, ListView

from ..models import Division, Heya, Rikishi


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
        queryset = (
            super()
            .get_queryset()
            .select_related("rank__division", "heya", "shusshin", "rank")
        )
        params = self.request.GET
        if params.get("include_retired") is None:
            queryset = queryset.filter(intai__isnull=True)
        if q := params.get("q"):
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(name_jp__icontains=q)
            )
        if heya := params.get("heya"):
            queryset = queryset.filter(heya__slug=heya)
        if division := params.get("division"):
            queryset = queryset.filter(rank__division__name=division)
        if params.get("international") is not None:
            queryset = queryset.filter(shusshin__international=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        include_retired = params.get("include_retired") is not None
        active_only = not include_retired
        context["active_only"] = active_only

        context["heyas"] = Heya.objects.all()
        context["divisions"] = Division.objects.all()
        context["query"] = params.get("q", "")
        context["selected_heya"] = params.get("heya", "")
        context["selected_division"] = params.get("division", "")
        context["international_only"] = params.get("international") is not None

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
