from django.conf import settings
from django.db import models

class TimeStampedModel(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: abstract=True

class ResearchGroup(TimeStampedModel):
    name=models.CharField(max_length=150, unique=True)
    description=models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
    def __str__(self): return self.name

class MemberProfile(TimeStampedModel):
    class MemberType(models.TextChoices):
        LECTURER='LECTURER','Dosen'
        STUDENT='STUDENT','Mahasiswa'
        ALUMNI='ALUMNI','Alumni'
        EXTERNAL='EXTERNAL','Eksternal'
    class Status(models.TextChoices):
        PENDING='PENDING','Menunggu Verifikasi'
        ACTIVE='ACTIVE','Aktif'
        INACTIVE='INACTIVE','Tidak Aktif'
        REJECTED='REJECTED','Ditolak'
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='member_profile')
    member_type=models.CharField(max_length=20, choices=MemberType.choices)
    status=models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    research_group=models.ForeignKey(ResearchGroup,null=True,blank=True,on_delete=models.SET_NULL)
    expertise=models.CharField(max_length=255, blank=True)
    generation=models.CharField(max_length=20, blank=True, help_text='Angkatan mahasiswa')
    program_study=models.CharField(max_length=120, blank=True)
    position=models.CharField(max_length=120, blank=True, help_text='Contoh: Kepala Lab, Asisten, Peneliti')
    joined_at=models.DateField(null=True, blank=True)
    notes=models.TextField(blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL, related_name='created_members')
    updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL, related_name='updated_members')
    class Meta:
        ordering=['user__first_name','user__last_name']
        indexes=[models.Index(fields=['status','member_type'])]
    def __str__(self): return self.user.get_full_name() or self.user.username

class MembershipHistory(TimeStampedModel):
    member=models.ForeignKey(MemberProfile,on_delete=models.CASCADE, related_name='histories')
    old_status=models.CharField(max_length=20, blank=True)
    new_status=models.CharField(max_length=20)
    changed_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
    reason=models.TextField(blank=True)
    def __str__(self): return f'{self.member} {self.old_status}->{self.new_status}'
