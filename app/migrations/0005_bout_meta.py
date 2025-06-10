from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_add_shikona_fields"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Bout",
                    fields=[],
                    options={
                        "verbose_name_plural": "Bouts",
                        "ordering": [
                            "basho__year",
                            "basho__month",
                            "day",
                            "match_no",
                        ],
                        "indexes": [
                            models.Index(
                                fields=["basho", "division", "day"],
                                name="bout_idx",
                            )
                        ],
                        "constraints": [
                            models.UniqueConstraint(
                                fields=[
                                    "basho",
                                    "day",
                                    "match_no",
                                    "east",
                                    "west",
                                ],
                                name="unique_bout",
                            )
                        ],
                    },
                )
            ],
            database_operations=[],
        )
    ]
