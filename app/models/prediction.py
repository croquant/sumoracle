from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .basho import Basho
from .rikishi import Rikishi


class Prediction(models.Model):
    """Predicted wins for a rikishi in a future ``Basho``."""

    pk = models.CompositePrimaryKey("rikishi_id", "basho_id")
    rikishi = models.ForeignKey(
        Rikishi,
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    basho = models.ForeignKey(
        Basho,
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    wins = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(15.0)]
    )

    class Meta:
        ordering = ["basho__year", "basho__month", "rikishi_id"]
        verbose_name_plural = "Predictions"
        constraints = [
            models.UniqueConstraint(
                fields=["rikishi", "basho"], name="unique_rikishi_prediction"
            )
        ]
        indexes = [models.Index(fields=["rikishi", "basho"])]

    def __str__(self):
        return f"{self.rikishi_id} {self.basho_id}: {self.wins}"
