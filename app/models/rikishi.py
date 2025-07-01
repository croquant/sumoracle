import pycountry
from django.db import models
from django.db.models import Case, IntegerField, Value, When
from django.utils.text import slugify

from libs.constants import RANKING_LEVELS

from .rank import Rank


class Heya(models.Model):
    """Stable to which a ``Rikishi`` belongs."""

    slug = models.SlugField(primary_key=True, editable=False)
    name = models.CharField(max_length=32, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Heya, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Heya"


class Shusshin(models.Model):
    """Place of origin for a ``Rikishi``."""

    slug = models.SlugField(primary_key=True, editable=False)
    name = models.CharField(max_length=32, editable=False)
    international = models.BooleanField(default=False, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Shusshin, self).save(*args, **kwargs)

    def flag(self):
        if self.international:
            try:
                return pycountry.countries.lookup(self.name).flag
            except LookupError:
                return "🏳️"
        return "🇯🇵"

    def __str__(self):
        return f"{self.flag()}{self.name}"

    class Meta:
        ordering = ["international", "name"]
        verbose_name_plural = "Shusshin"


class RikishiQuerySet(models.QuerySet):
    def banzuke(self):
        level_case = Case(
            *[
                When(rank__title=title, then=Value(level))
                for title, level in RANKING_LEVELS.items()
            ],
            default=Value(99),
            output_field=IntegerField(),
        )
        missing_case = Case(
            When(rank__isnull=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
        return self.annotate(
            rank_level=level_case, rank_missing=missing_case
        ).order_by(
            "rank_missing",
            "rank__division__level",
            "rank_level",
            "rank__order",
            "rank__direction",
            "name",
        )


class RikishiManager(models.Manager.from_queryset(RikishiQuerySet)):
    def get_queryset(self):
        return super().get_queryset().banzuke()


class Rikishi(models.Model):
    """Sumo wrestler with optional ``Rank``, ``Heya`` and ``Shusshin`` links."""

    id = models.PositiveSmallIntegerField(primary_key=True, editable=False)
    sumodb_id = models.PositiveSmallIntegerField(
        unique=True, blank=True, null=True
    )
    nsk_id = models.PositiveSmallIntegerField(
        unique=True, blank=True, null=True
    )
    name = models.CharField(max_length=64)
    name_jp = models.CharField(max_length=64)
    rank = models.ForeignKey(
        Rank,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="rikishi",
    )
    heya = models.ForeignKey(
        Heya,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="rikishi",
    )
    shusshin = models.ForeignKey(
        Shusshin,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="rikishi",
    )
    height = models.DecimalField(
        max_digits=4, decimal_places=1, blank=True, null=True
    )
    weight = models.DecimalField(
        max_digits=4, decimal_places=1, blank=True, null=True
    )
    birth_date = models.DateField(blank=True, null=True)
    debut = models.DateField(blank=True, null=True)
    intai = models.DateField(blank=True, null=True)

    objects = RikishiManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Rikishi"
