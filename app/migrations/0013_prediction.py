import django.db.models.deletion
from django.core import validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0012_rename_app_bashora_rikishi_e02e83_idx_app_bashora_rikishi_811c00_idx_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Prediction",
            fields=[
                (
                    "pk",
                    models.CompositePrimaryKey(
                        "rikishi_id",
                        "basho_id",
                        blank=True,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "wins",
                    models.FloatField(
                        validators=[
                            validators.MinValueValidator(0.0),
                            validators.MaxValueValidator(15.0),
                        ]
                    ),
                ),
                (
                    "basho",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="predictions",
                        to="app.basho",
                    ),
                ),
                (
                    "rikishi",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="predictions",
                        to="app.rikishi",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Predictions",
                "ordering": ["basho__year", "basho__month", "rikishi_id"],
                "indexes": [
                    models.Index(fields=["rikishi", "basho"], name="app_predic_rikishi_basho_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("rikishi", "basho"),
                        name="unique_rikishi_prediction",
                    ),
                ],
            },
        ),
    ]
