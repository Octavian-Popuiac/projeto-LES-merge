from django.contrib import admin
from .models import GroupMetadata

class GroupMetadataAdmin(admin.ModelAdmin):
    list_display = ('group', 'description', 'created_by', 'created_at')
    search_fields = ('group__name', 'description')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(GroupMetadata, GroupMetadataAdmin)