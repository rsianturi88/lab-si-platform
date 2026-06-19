from django import forms
from .models import *

class BootstrapFormMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class','form-control')

class ResearchProjectForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=ResearchProject
        fields='__all__'
        exclude=['created_by']
        widgets={'abstract':forms.Textarea(attrs={'rows':4}),'expected_outputs':forms.Textarea(attrs={'rows':3}),'risks':forms.Textarea(attrs={'rows':3})}
class CommunityServiceProjectForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=CommunityServiceProject
        fields='__all__'
        exclude=['created_by']
class PublicationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=Publication
        fields='__all__'
class PartnerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=Partner
        fields='__all__'
class CollaborationAgreementForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=CollaborationAgreement
        fields='__all__'
class LabAssetForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=LabAsset
        fields='__all__'
class RoomBookingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=RoomBooking
        fields='__all__'
        widgets={'start_time':forms.DateTimeInput(attrs={'type':'datetime-local'}),'end_time':forms.DateTimeInput(attrs={'type':'datetime-local'})}
class KPIRecordForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=KPIRecord
        fields='__all__'
class DatasetForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=Dataset
        fields='__all__'
class SourceCodeRepositoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=SourceCodeRepository
        fields='__all__'
class LabPositionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=LabPosition
        fields='__all__'
class OrganizationUnitForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=OrganizationUnit
        fields='__all__'

class ProfessionalServiceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=ProfessionalService
        exclude=['created_by']
        widgets={'description':forms.Textarea(attrs={'rows':4}),'deliverables':forms.Textarea(attrs={'rows':3}),'notes':forms.Textarea(attrs={'rows':3}),'start_date':forms.DateInput(attrs={'type':'date'}),'end_date':forms.DateInput(attrs={'type':'date'})}
class QualityCycleRecordForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=QualityCycleRecord
        fields='__all__'
        widgets={'standard':forms.Textarea(attrs={'rows':3}),'implementation_summary':forms.Textarea(attrs={'rows':3}),'evaluation_findings':forms.Textarea(attrs={'rows':3}),'corrective_action':forms.Textarea(attrs={'rows':3}),'due_date':forms.DateInput(attrs={'type':'date'})}
class WorkPlanBudgetForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=WorkPlanBudget
        fields='__all__'
class SOPDocumentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=SOPDocument
        fields='__all__'
        widgets={'effective_date':forms.DateInput(attrs={'type':'date'}),'review_date':forms.DateInput(attrs={'type':'date'}),'description':forms.Textarea(attrs={'rows':4})}
class PracticumCourseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=PracticumCourse
        fields='__all__'
        widgets={'implementation_notes':forms.Textarea(attrs={'rows':3}),'evaluation_summary':forms.Textarea(attrs={'rows':3})}
class CurriculumSupportForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=CurriculumSupport
        fields='__all__'
        widgets={'recommendation':forms.Textarea(attrs={'rows':5})}
class RoadmapItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=RoadmapItem
        fields='__all__'
        widgets={'alignment_policy':forms.Textarea(attrs={'rows':3}),'expected_outputs':forms.Textarea(attrs={'rows':3})}
class TalentProgramForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=TalentProgram
        fields='__all__'
        widgets={'selection_criteria':forms.Textarea(attrs={'rows':3}),'mentoring_plan':forms.Textarea(attrs={'rows':3}),'result_summary':forms.Textarea(attrs={'rows':3})}
class DigitalChannelForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=DigitalChannel
        fields='__all__'
        widgets={'last_update':forms.DateInput(attrs={'type':'date'}),'content_strategy':forms.Textarea(attrs={'rows':3}),'performance_notes':forms.Textarea(attrs={'rows':3})}
class SatisfactionSurveyForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=SatisfactionSurvey
        fields='__all__'
        widgets={'summary':forms.Textarea(attrs={'rows':3}),'follow_up':forms.Textarea(attrs={'rows':3})}
class PerformanceReportForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=PerformanceReport
        fields='__all__'
        widgets={'submitted_at':forms.DateInput(attrs={'type':'date'}),'executive_summary':forms.Textarea(attrs={'rows':5})}
class HeadApprovalForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model=HeadApproval
        fields='__all__'
        widgets={'requested_at':forms.DateInput(attrs={'type':'date'}),'decided_at':forms.DateInput(attrs={'type':'date'}),'rationale':forms.Textarea(attrs={'rows':3}),'decision_notes':forms.Textarea(attrs={'rows':3})}
