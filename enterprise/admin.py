from django.contrib import admin
from .models import *

@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display=('title','scheme','status','leader','budget','start_date','end_date')
    list_filter=('scheme','status','research_group')
    search_fields=('title','keywords','leader__user__first_name','leader__user__last_name')
    filter_horizontal=('members',)
@admin.register(CommunityServiceProject)
class CommunityServiceProjectAdmin(admin.ModelAdmin):
    list_display=('title','partner_name','status','leader','budget','start_date')
    list_filter=('status',)
    search_fields=('title','partner_name')
    filter_horizontal=('members',)
@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display=('title','publication_type','indexing','year','venue','citation_count')
    list_filter=('publication_type','indexing','year')
    search_fields=('title','venue','doi')
    filter_horizontal=('authors',)
@admin.register(KPIRecord)
class KPIRecordAdmin(admin.ModelAdmin):
    list_display=('name','category','year','target_value','actual_value','unit')
    list_filter=('category','year')
for model in [OrganizationUnit,LabPosition,FundingSource,Dataset,SourceCodeRepository,Partner,CollaborationAgreement,LabAsset,RoomBooking,ProfessionalService,QualityCycleRecord,WorkPlanBudget,SOPDocument,PracticumCourse,CurriculumSupport,RoadmapItem,TalentProgram,DigitalChannel,SatisfactionSurvey,PerformanceReport,HeadApproval]:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
