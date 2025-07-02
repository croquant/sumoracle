from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_rikishi_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='bashohistory',
            name='glicko',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
