from django.db import models
from django.utils.text import slugify

from app.constants import (
    BASHO_NAMES,
    DIRECTION_NAMES,
    DIRECTION_NAMES_SHORT,
    RANK_NAMES,
    RANK_NAMES_SHORT,
    RANKING_LEVELS,
)


class Rank(models.Model):
    slug = models.SlugField(primary_key=True, editable=False)
    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="ranks",
        editable=False,
    )
    title = models.CharField(max_length=12, choices=RANK_NAMES, editable=False)
    level = models.PositiveSmallIntegerField(editable=False)
    order = models.PositiveSmallIntegerField(blank=True, null=True, editable=False)
    direction = models.CharField(
        max_length=4,
        choices=DIRECTION_NAMES,
        blank=True,
        null=True,
        editable=False,
    )

    def name(self):
        if self.order and self.direction:
            dir_shorthand = DIRECTION_NAMES_SHORT[self.direction]
            return f"{self.title} {self.order}{dir_shorthand}"
        else:
            return self.title

    def long_name(self):
        if self.order and self.direction:
            return f"{self.title} {self.order} {self.direction}"
        else:
            return self.title

    def short_name(self):
        shorthand = RANK_NAMES_SHORT[self.title]
        if self.order and self.direction:
            dir_shorthand = DIRECTION_NAMES_SHORT[self.direction]
            return f"{shorthand}{self.order}{dir_shorthand}"
        else:
            return shorthand

    def save(self, *args, **kwargs):
        self.slug = slugify(self.long_name())
        if Division.objects.filter(name=self.title).exists():
            self.division = Division.objects.get(name=self.title)
        else:
            self.division = Division.objects.get(name="Makuuchi")
        self.level = RANKING_LEVELS[self.title]
        super(Rank, self).save(*args, **kwargs)

    def __str__(self):
        return self.name()

    class Meta:
        ordering = ["level", "order", "direction"]


class Basho(models.Model):
    YEAR_CHOICES = [(y, str(y)) for y in range(1958, 2100)]
    MONTH_CHOICES = [
        (1, "January"),
        (3, "March"),
        (5, "May"),
        (7, "July"),
        (9, "September"),
        (11, "November"),
    ]

    slug = models.CharField(max_length=6, primary_key=True, editable=False)
    year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, editable=False)
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES, editable=False)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def name(self):
        return BASHO_NAMES[self.month]

    def __str__(self):
        return f"{self.name()} {self.year}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["year", "month"], name="unique_basho"),
        ]
        indexes = [
            models.Index(fields=["year", "month"]),
        ]
        verbose_name_plural = "Basho"
