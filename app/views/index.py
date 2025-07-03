from django.views.generic import TemplateView

from ..models import Basho, Division, Rikishi


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["division_count"] = Division.objects.count()
        context["rikishi_count"] = Rikishi.objects.filter(
            intai__isnull=True
        ).count()
        context["latest_basho"] = Basho.objects.order_by(
            "-year",
            "-month",
        ).first()
        return context
