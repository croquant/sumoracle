from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0005_bout_meta"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Basho",
                    fields=[],
                    options={
                        "verbose_name_plural": "Basho",
                        "indexes": [
                            models.Index(fields=["year", "month"], name="basho_year_month_idx"),
                        ],
                        "constraints": [
                            models.UniqueConstraint(fields=["year", "month"], name="unique_basho"),
                        ],
                    },
                ),
                migrations.CreateModel(
                    name="Heya",
                    fields=[],
                    options={
                        "ordering": ["name"],
                        "verbose_name_plural": "Heya",
                    },
                ),
                migrations.CreateModel(
                    name="Rank",
                    fields=[],
                    options={
                        "ordering": ["division__level", "level", "order", "direction"],
                        "unique_together": {("title", "order", "direction", "division")},
                    },
                ),
                migrations.CreateModel(
                    name="Rikishi",
                    fields=[],
                    options={
                        "ordering": ["name"],
                        "verbose_name_plural": "Rikishi",
                    },
                ),
                migrations.CreateModel(
                    name="Shusshin",
                    fields=[],
                    options={
                        "ordering": ["international", "name"],
                        "verbose_name_plural": "Shusshin",
                    },
                ),
            ],
            database_operations=[],
        )
    ]
