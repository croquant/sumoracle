from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Division(models.Model):
    name = models.CharField(
        verbose_name="name", primary_key=True, max_length=12, unique=True
    )
    name_short = models.CharField(
        verbose_name="short name", max_length=2, unique=True
    )
    level = models.PositiveSmallIntegerField(verbose_name="level", unique=True)

    class Meta:
        verbose_name = "division"
        verbose_name_plural = "divisions"
        ordering = ["level"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("division-detail", args=[slugify(self.name)])
