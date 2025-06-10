from django.db import models

from .basho import Basho
from .rank import Rank
from .rikishi import Rikishi


class BashoHistory(models.Model):
    """Ranking and measurements for a rikishi in a specific ``Basho``."""

    pk = models.CompositePrimaryKey("rikishi_id", "basho_id")
    rikishi = models.ForeignKey(
        Rikishi,
        on_delete=models.CASCADE,
        related_name="ranking_history",
    )
    basho = models.ForeignKey(
        Basho, on_delete=models.CASCADE, related_name="ranking"
    )
    rank = models.ForeignKey(
        Rank,
        on_delete=models.CASCADE,
    )
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    shikona_en = models.CharField(max_length=64, blank=True, default="")
    shikona_jp = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ["basho__year", "basho__month", "rikishi_id"]
        verbose_name_plural = "Basho history"
        constraints = [
            models.UniqueConstraint(
                fields=["rikishi", "basho"],
                name="unique_rikishi_basho",
            )
        ]
        indexes = [
            models.Index(fields=["rikishi", "basho"]),
        ]
