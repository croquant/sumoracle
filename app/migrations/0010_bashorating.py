import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_rikishi_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='BashoRating',
            fields=[
                ('pk', models.CompositePrimaryKey('rikishi_id', 'basho_id', blank=True, editable=False, primary_key=True, serialize=False)),
                ('rating', models.FloatField()),
                ('rd', models.FloatField()),
                ('vol', models.FloatField()),
                ('basho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='app.basho')),
                ('rikishi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating_history', to='app.rikishi')),
            ],
            options={
                'verbose_name_plural': 'Basho ratings',
                'ordering': ['basho__year', 'basho__month', 'rikishi_id'],
                'indexes': [models.Index(fields=['rikishi', 'basho'], name='app_bashora_rikishi_e02e83_idx')],
                'constraints': [models.UniqueConstraint(fields=('rikishi', 'basho'), name='unique_rikishi_rating')],
            },
        ),
    ]

