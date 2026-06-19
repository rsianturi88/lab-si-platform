from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import render
from .models import AuditLog
@login_required
def audit_logs(request):
    if not request.user.can_audit(): return HttpResponseForbidden('Anda tidak memiliki akses audit log.')
    qs=AuditLog.objects.select_related('user').all()
    page=Paginator(qs,25).get_page(request.GET.get('page'))
    return render(request,'audit/logs.html',{'page':page})
