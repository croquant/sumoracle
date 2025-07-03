from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0010_bashorating"),
    ]

    operations = [
        migrations.AddField(
            model_name="bashorating",
            name="previous_rating",
            field=models.FloatField(default=1500.0),
        ),
        migrations.AddField(
            model_name="bashorating",
            name="previous_rd",
            field=models.FloatField(default=350.0),
        ),
        migrations.AddField(
            model_name="bashorating",
            name="previous_vol",
            field=models.FloatField(default=0.11),
        ),
    ]
