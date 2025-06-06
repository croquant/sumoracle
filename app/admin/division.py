from django.contrib import admin

from ..models import Division


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ["name", "name_short", "level"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
