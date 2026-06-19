from django import forms
from .models import LabActivity
class LabActivityForm(forms.ModelForm):
    class Meta:
        model=LabActivity
        fields=['title','activity_type','description','start_date','end_date','location','participants']
        widgets={'start_date':forms.DateInput(attrs={'type':'date'}),'end_date':forms.DateInput(attrs={'type':'date'}),'participants':forms.CheckboxSelectMultiple}
