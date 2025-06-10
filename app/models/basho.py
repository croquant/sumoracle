from django.db import models

from app.constants import BASHO_NAMES


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
    year = models.PositiveSmallIntegerField(
        choices=YEAR_CHOICES, editable=False
    )
    month = models.PositiveSmallIntegerField(
        choices=MONTH_CHOICES, editable=False
    )

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.year}{self.month:02d}"
        super().save(*args, **kwargs)

    def name(self):
        return BASHO_NAMES[self.month]

    def __str__(self):
        return f"{self.name()} {self.year}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["year", "month"], name="unique_basho"
            ),
        ]
        indexes = [
            models.Index(fields=["year", "month"]),
        ]
        verbose_name_plural = "Basho"
