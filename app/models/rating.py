from django.db import models

from .basho import Basho
from .rikishi import Rikishi


class BashoRating(models.Model):
    """Glicko rating statistics for a rikishi in a specific ``Basho``."""

    pk = models.CompositePrimaryKey("rikishi_id", "basho_id")
    rikishi = models.ForeignKey(
        Rikishi,
        on_delete=models.CASCADE,
        related_name="rating_history",
    )
    basho = models.ForeignKey(
        Basho,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    rating = models.FloatField()
    rd = models.FloatField()
    vol = models.FloatField()

    class Meta:
        ordering = ["basho__year", "basho__month", "rikishi_id"]
        verbose_name_plural = "Basho ratings"
        constraints = [
            models.UniqueConstraint(
                fields=["rikishi", "basho"],
                name="unique_rikishi_rating",
            )
        ]
        indexes = [models.Index(fields=["rikishi", "basho"])]
