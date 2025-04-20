from django.contrib import admin
from .models import Discrepancy

@admin.register(Discrepancy)
class DiscrepancyAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "status", "created_at")
    list_filter = ("status", "project")
    search_fields = ("document__text",)