from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_populate_divisions"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="BashoHistory",
                    fields=[],
                    options={
                        "ordering": ["basho__year", "basho__month", "rikishi_id"],
                        "verbose_name_plural": "Basho history",
                        "indexes": [
                            models.Index(
                                fields=["rikishi", "basho"],
                                name="bashohistory_rikishi_basho_idx",
                            )
                        ],
                        "constraints": [
                            models.UniqueConstraint(
                                fields=["rikishi", "basho"],
                                name="unique_rikishi_basho",
                            )
                        ],
                    },
                )
            ],
            database_operations=[],
        )
    ]

