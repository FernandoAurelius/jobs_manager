# workflow/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin

from workflow.forms import StaffChangeForm, StaffCreationForm
from workflow.models import CompanyDefaults, Staff


@admin.register(CompanyDefaults)
class CompanyDefaultsAdmin(admin.ModelAdmin):
    def edit_link(self, obj):
        from django.utils.html import format_html
        return format_html('<a href="{}/change/">Edit defaults</a>', obj.pk)
    
    edit_link.short_description = 'Actions'
    edit_link.allow_tags = True

    list_display = ["edit_link", "charge_out_rate", "wage_rate", "time_markup", "materials_markup", "starting_job_number"]
    
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "time_markup",
                    "materials_markup",
                    "charge_out_rate",
                    "wage_rate",
                    "starting_job_number"
                )
            },
        ),
        (
            "Working Hours",
            {
                "fields": (
                    ("mon_start", "mon_end"),
                    ("tue_start", "tue_end"),
                    ("wed_start", "wed_end"),
                    ("thu_start", "thu_end"),
                    ("fri_start", "fri_end"),
                )
            },
        ),
        (
            "Xero Integration",
            {
                "fields": (
                    "xero_tenant_id",
                    "last_xero_sync",
                    "last_xero_deep_sync",
                ),
                "description": "To force a deep sync, clear the 'last_xero_deep_sync' field or set it to a date more than 30 days ago.",
            },
        ),
    )


@admin.register(Staff)
class StaffAdmin(UserAdmin, SimpleHistoryAdmin):
    add_form = StaffCreationForm
    form = StaffChangeForm
    model = Staff
    
    list_display = (
        "email", 
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "id"
    )
    list_filter = (
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "preferred_name",
                    "wage_rate",
                    "ims_payroll_id",
                )
            },
        ),
        (
            "Working Hours",
            {
                "fields": (
                    "hours_mon",
                    "hours_tue",
                    "hours_wed",
                    "hours_thu",
                    "hours_fri",
                    "hours_sat",
                    "hours_sun",
                ),
                "description": "Set standard working hours for each day of the week. Use 0 for non-working days.",
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "preferred_name",
                    "wage_rate",
                    "ims_payroll_id",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
