from django.contrib import admin
from .models import ResearchGroup, MemberProfile, MembershipHistory
@admin.register(ResearchGroup)
class ResearchGroupAdmin(admin.ModelAdmin): list_display=('name','is_active','created_at')
@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display=('user','member_type','status','research_group','program_study','position','updated_at')
    list_filter=('member_type','status','research_group')
    search_fields=('user__username','user__first_name','user__last_name','user__email','user__institution_id','expertise')
@admin.register(MembershipHistory)
class MembershipHistoryAdmin(admin.ModelAdmin): list_display=('member','old_status','new_status','changed_by','created_at')
