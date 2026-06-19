from django import forms
from .models import User
from memberships.models import MemberProfile, ResearchGroup

class ProfileForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','email','phone','institution_id']

class SelfMemberProfileForm(forms.ModelForm):
    class Meta:
        model=MemberProfile
        fields=['member_type','research_group','expertise','generation','program_study','position','joined_at','notes']
        widgets={'joined_at':forms.DateInput(attrs={'type':'date'})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # Status hanya boleh diubah pengelola, bukan pengguna biasa.
        self.fields['member_type'].disabled=True

class AdminUserCreateForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput, min_length=10, initial='ChangeMe123!')
    create_member_profile=forms.BooleanField(required=False, initial=True, label='Buat profil keanggotaan')
    member_type=forms.ChoiceField(choices=MemberProfile.MemberType.choices, initial=MemberProfile.MemberType.STUDENT, required=False)
    research_group=forms.ModelChoiceField(queryset=ResearchGroup.objects.filter(is_active=True), required=False)
    expertise=forms.CharField(max_length=255, required=False)
    program_study=forms.CharField(max_length=120, required=False)
    generation=forms.CharField(max_length=20, required=False)
    class Meta:
        model=User
        fields=['username','first_name','last_name','email','phone','institution_id','role','is_active','is_verified']
    def clean_username(self):
        v=self.cleaned_data['username']
        if User.objects.filter(username=v).exists(): raise forms.ValidationError('Username sudah digunakan.')
        return v
    def clean_email(self):
        v=self.cleaned_data.get('email')
        if v and User.objects.filter(email=v).exists(): raise forms.ValidationError('Email sudah digunakan.')
        return v

class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','first_name','last_name','email','phone','institution_id','role','is_active','is_staff','is_verified']
    def __init__(self,*args,**kwargs):
        self.instance_user = kwargs.get('instance')
        super().__init__(*args,**kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class','form-control')
    def clean_username(self):
        v=self.cleaned_data['username']
        qs=User.objects.filter(username=v)
        if self.instance and self.instance.pk:
            qs=qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Username sudah digunakan.')
        return v
    def clean_email(self):
        v=self.cleaned_data.get('email')
        if v:
            qs=User.objects.filter(email=v)
            if self.instance and self.instance.pk:
                qs=qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Email sudah digunakan.')
        return v

class AdminPasswordResetForm(forms.Form):
    password=forms.CharField(widget=forms.PasswordInput, min_length=10, label='Password baru')
