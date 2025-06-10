from django.db import migrations

from app.constants import DivisionEnum


def populate_divisions(apps, schema_editor):
    Division = apps.get_model("app", "Division")
    for division in DivisionEnum:
        Division.objects.create(
            name=division.label,
            name_short=division.short,
            level=division.level,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_division"),
    ]

    operations = [
        migrations.RunPython(populate_divisions),
    ]
