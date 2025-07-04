from django.db import models

from libs.constants import (
    DIRECTION_NAMES_SHORT,
    RANK_NAMES_SHORT,
    Direction,
    RankName,
)

from .division import Division


class Rank(models.Model):
    """Individual rank within a ``Division`` including order and direction."""

    slug = models.SlugField(primary_key=True, editable=False)

    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="ranks",
        editable=False,
    )
    title = models.CharField(
        max_length=20, choices=RankName.choices, editable=False
    )
    order = models.PositiveSmallIntegerField(
        null=True, blank=True, editable=False
    )
    direction = models.CharField(
        max_length=4,
        choices=Direction.choices,
        null=True,
        blank=True,
        editable=False,
    )

    def __init__(self, *args, **kwargs):
        self.level = kwargs.pop("level", None)
        super().__init__(*args, **kwargs)

    @property
    def value(self):
        dir_val = (
            0
            if self.direction == "East"
            else 1
            if self.direction == "West"
            else 0
        )
        return self.division.level * 10000 + (self.order or 0) * 2 + dir_val

    class Meta:
        unique_together = ("title", "order", "direction", "division")
        ordering = ["division__level", "order", "direction"]

    def __str__(self):
        return self.name()

    def name(self):
        if self.order and self.direction:
            dir_shorthand = DIRECTION_NAMES_SHORT.get(self.direction, "")
            return f"{self.title} {self.order}{dir_shorthand}"
        return self.title

    def long_name(self):
        if self.order and self.direction:
            return f"{self.title} {self.order} {self.direction}"
        return self.title

    def short_name(self):
        shorthand = RANK_NAMES_SHORT.get(self.title, self.title)
        if self.order and self.direction:
            dir_shorthand = DIRECTION_NAMES_SHORT.get(self.direction, "")
            return f"{shorthand}{self.order}{dir_shorthand}"
        return shorthand
