from django.contrib import admin

from ..models import Bout


@admin.register(Bout)
class BoutAdmin(admin.ModelAdmin):
    list_display = [
        "basho",
        "division",
        "day",
        "match_no",
        "east",
        "west",
        "winner",
    ]
