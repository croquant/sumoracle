from django.db import models

from .basho import Basho
from .division import Division
from .rikishi import Rikishi


class Bout(models.Model):
    """A single bout between two rikishi in a given Basho."""

    basho = models.ForeignKey(
        Basho,
        on_delete=models.CASCADE,
        related_name="bouts",
    )
    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="bouts",
    )
    day = models.PositiveSmallIntegerField()
    match_no = models.PositiveSmallIntegerField()
    east = models.ForeignKey(
        Rikishi,
        on_delete=models.CASCADE,
        related_name="bouts_as_east",
    )
    west = models.ForeignKey(
        Rikishi,
        on_delete=models.CASCADE,
        related_name="bouts_as_west",
    )
    east_shikona = models.CharField(max_length=64)
    west_shikona = models.CharField(max_length=64)
    kimarite = models.CharField(max_length=32)
    winner = models.ForeignKey(
        Rikishi,
        on_delete=models.CASCADE,
        related_name="bouts_won",
    )

    class Meta:
        ordering = ["basho__year", "basho__month", "day", "match_no"]
        verbose_name_plural = "Bouts"
        constraints = [
            models.UniqueConstraint(
                fields=["basho", "day", "match_no", "east", "west"],
                name="unique_bout",
            )
        ]
        indexes = [models.Index(fields=["basho", "division", "day"])]

    def __str__(self):
        return (
            f"{self.basho.slug} Day {self.day} No.{self.match_no}: "
            f"{self.east_shikona} vs {self.west_shikona}"
        )
