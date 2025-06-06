import pycountry
from django.db import models
from django.utils.text import slugify

from .shared import Rank


class Heya(models.Model):
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
    slug = models.SlugField(primary_key=True, editable=False)
    name = models.CharField(max_length=32, editable=False)
    international = models.BooleanField(default=False, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Shusshin, self).save(*args, **kwargs)

    def flag(self):
        if self.international:
            return pycountry.countries.lookup(self.name).flag
        else:
            return "🇯🇵"

    def __str__(self):
        return f"{self.flag()}{self.name}"

    class Meta:
        ordering = ["international", "name"]
        verbose_name_plural = "Shusshin"


class Rikishi(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, editable=False)
    sumodb_id = models.PositiveSmallIntegerField(unique=True, blank=True, null=True)
    nsk_id = models.PositiveSmallIntegerField(unique=True, blank=True, null=True)
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
    height = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    weight = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    debut = models.DateField(blank=True, null=True)
    intai = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Rikishi"
