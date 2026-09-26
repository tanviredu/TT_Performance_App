from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.urls import path

from .exports import export_equipment_hours_to_excel
from .models import Equipment, EquipmentHourRecord, Operator


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ("operator_id", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("operator_id", "name")
    list_editable = ("is_active",)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("equipment_id", "initial_hours", "is_active")
    list_filter = ("is_active",)
    search_fields = ("equipment_id",)
    list_editable = ("initial_hours", "is_active")


@admin.register(EquipmentHourRecord)
class EquipmentHourRecordAdmin(admin.ModelAdmin):
    change_list_template = "admin/equipment/equipmenthourrecord/change_list.html"
    list_display = (
        "id",
        "date",
        "operator",
        "equipment",
        "previous_hours",
        "total_hours",
        "shift_hours",
        "created_at",
    )
    list_filter = ("date", "equipment", "operator")
    search_fields = (
        "operator__operator_id",
        "operator__name",
        "equipment__equipment_id",
    )
    date_hierarchy = "date"
    readonly_fields = ("date", "previous_hours", "shift_hours", "created_at")
    list_select_related = ("operator", "equipment")
    actions = ["export_to_excel"]

    @admin.action(description="Export selected to Excel")
    def export_to_excel(self, request, queryset):
        return export_equipment_hours_to_excel(
            queryset, filename_prefix="equipment_hours_selected"
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "export-excel/",
                self.admin_site.admin_view(self.export_excel_changelist_view),
                name="equipment_equipmenthourrecord_export_excel",
            ),
        ]
        return custom_urls + urls

    def export_excel_changelist_view(self, request):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        cl = self.get_changelist_instance(request)
        queryset = cl.get_queryset(request)
        return export_equipment_hours_to_excel(
            queryset, filename_prefix="equipment_hours"
        )