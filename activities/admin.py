from django.contrib import admin
from .models import LabActivity
@admin.register(LabActivity)
class LabActivityAdmin(admin.ModelAdmin):
    list_display=('title','activity_type','start_date','location','created_by')
    list_filter=('activity_type','start_date')
    search_fields=('title','description','location')
