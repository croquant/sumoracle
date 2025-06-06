from django.db import models

from .basho import Basho
from .rank import Rank
from .rikishi import Rikishi


class BashoHistory(models.Model):
    pk = models.CompositePrimaryKey("rikishi_id", "basho_id")
    rikishi = models.ForeignKey(
        Rikishi,
        on_delete=models.CASCADE,
        related_name="ranking_history",
    )
    basho = models.ForeignKey(Basho, on_delete=models.CASCADE, related_name="ranking")
    rank = models.ForeignKey(
        Rank,
        on_delete=models.CASCADE,
    )
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
