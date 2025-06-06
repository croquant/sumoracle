from django.db import models

from app.constants import (DIRECTION_NAMES, DIRECTION_NAMES_SHORT, RANK_NAMES,
                           RANK_NAMES_SHORT)

from .division import Division


class Rank(models.Model):
    slug = models.SlugField(primary_key=True, editable=False)

    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="ranks",
        editable=False,
    )
    title = models.CharField(max_length=20, choices=RANK_NAMES, editable=False)
    level = models.PositiveSmallIntegerField(editable=False)
    order = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    direction = models.CharField(
        max_length=4,
        choices=DIRECTION_NAMES,
        null=True,
        blank=True,
        editable=False,
    )
    value = models.GeneratedField(
        expression=(
            models.F("division__level") * models.Value(10000)
            + models.F("level") * models.Value(100)
            + models.functions.Coalesce(models.F("order"), models.Value(0))
            * models.Value(2)
            + models.Case(
                models.When(direction="East", then=models.Value(0)),
                models.When(direction="West", then=models.Value(1)),
                default=models.Value(0),
                output_field=models.IntegerField(),
            )
        ),
        output_field=models.IntegerField(),
        db_persist=True,  # stored (not virtual)
        editable=False,
    )

    class Meta:
        unique_together = ("title", "order", "direction", "division")
        ordering = ["division__level", "level", "order", "direction"]

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
