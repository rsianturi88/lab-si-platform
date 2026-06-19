from django import forms
from django.contrib.auth import get_user_model
from .models import MemberProfile, ResearchGroup
User=get_user_model()
class MemberCreateForm(forms.Form):
    username=forms.CharField(max_length=150)
    email=forms.EmailField()
    first_name=forms.CharField(max_length=150)
    last_name=forms.CharField(max_length=150, required=False)
    institution_id=forms.CharField(max_length=50, required=False, label='NIP/NIDN/NIM')
    member_type=forms.ChoiceField(choices=MemberProfile.MemberType.choices)
    status=forms.ChoiceField(choices=MemberProfile.Status.choices, initial='ACTIVE')
    research_group=forms.ModelChoiceField(queryset=ResearchGroup.objects.filter(is_active=True), required=False)
    expertise=forms.CharField(max_length=255, required=False)
    generation=forms.CharField(max_length=20, required=False)
    program_study=forms.CharField(max_length=120, required=False)
    position=forms.CharField(max_length=120, required=False)
    def clean_username(self):
        v=self.cleaned_data['username']
        if User.objects.filter(username=v).exists(): raise forms.ValidationError('Username sudah digunakan.')
        return v
    def clean_email(self):
        v=self.cleaned_data['email']
        if User.objects.filter(email=v).exists(): raise forms.ValidationError('Email sudah digunakan.')
        return v
class MemberProfileForm(forms.ModelForm):
    class Meta:
        model=MemberProfile
        fields=['member_type','status','research_group','expertise','generation','program_study','position','joined_at','notes']
        widgets={'joined_at':forms.DateInput(attrs={'type':'date'})}
class ResearchGroupForm(forms.ModelForm):
    class Meta:
        model=ResearchGroup
        fields=['name','description','is_active']
