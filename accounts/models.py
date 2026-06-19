from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN='SUPERADMIN','Super Admin'
        LAB_HEAD='LAB_HEAD','Kepala Lab'
        LECTURER='LECTURER','Dosen'
        STUDENT='STUDENT','Mahasiswa'
        ADMIN='ADMIN','Admin'
        AUDITOR='AUDITOR','Auditor'
    role=models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone=models.CharField(max_length=30, blank=True)
    institution_id=models.CharField(max_length=50, blank=True, help_text='NIP/NIDN/NIM')
    is_verified=models.BooleanField(default=False)

    def can_manage_members(self):
        return self.is_superuser or self.role in [self.Role.SUPERADMIN,self.Role.LAB_HEAD,self.Role.ADMIN]
    def can_audit(self):
        return self.is_superuser or self.role in [self.Role.SUPERADMIN,self.Role.LAB_HEAD,self.Role.AUDITOR]
    def can_manage_enterprise(self):
        return self.is_superuser or self.role in [self.Role.SUPERADMIN,self.Role.LAB_HEAD,self.Role.ADMIN,self.Role.LECTURER]
