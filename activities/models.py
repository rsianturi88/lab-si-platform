from django.conf import settings
from django.db import models
from memberships.models import TimeStampedModel, MemberProfile
class LabActivity(TimeStampedModel):
    class ActivityType(models.TextChoices):
        RESEARCH='RESEARCH','Riset'
        SERVICE='SERVICE','Pengabdian'
        TRAINING='TRAINING','Pelatihan'
        INTERNAL='INTERNAL','Internal Lab'
        INDUSTRY='INDUSTRY','Kolaborasi Industri'
    title=models.CharField(max_length=200)
    activity_type=models.CharField(max_length=20, choices=ActivityType.choices)
    description=models.TextField(blank=True)
    start_date=models.DateField()
    end_date=models.DateField(null=True, blank=True)
    location=models.CharField(max_length=200, blank=True)
    participants=models.ManyToManyField(MemberProfile, blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
    class Meta: ordering=['-start_date']; indexes=[models.Index(fields=['activity_type','start_date'])]
    def __str__(self): return self.title
