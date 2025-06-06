from django.db import migrations

from app.constants import DIVISIONS


def populate_divisions(apps, schema_editor):
    Division = apps.get_model("app", "Division")
    for name, name_short, level in DIVISIONS:
        Division.objects.create(name=name, name_short=name_short, level=level)


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_division"),
    ]

    operations = [
        migrations.RunPython(populate_divisions),
    ]
