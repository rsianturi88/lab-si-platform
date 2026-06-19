from django.conf import settings
from django.db import models
class AuditLog(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
    action=models.CharField(max_length=120)
    path=models.CharField(max_length=500, blank=True)
    method=models.CharField(max_length=10, blank=True)
    ip_address=models.GenericIPAddressField(null=True, blank=True)
    user_agent=models.TextField(blank=True)
    metadata=models.JSONField(default=dict, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']
        indexes=[models.Index(fields=['created_at']), models.Index(fields=['action'])]
    def __str__(self): return f'{self.created_at} {self.action}'
