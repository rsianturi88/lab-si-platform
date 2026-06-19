from .models import AuditLog
class AuditMiddleware:
    def __init__(self, get_response): self.get_response=get_response
    def __call__(self, request):
        response=self.get_response(request)
        if request.user.is_authenticated and request.method in ['POST','PUT','PATCH','DELETE']:
            ip=request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR','')).split(',')[0]
            AuditLog.objects.create(user=request.user, action=f'{request.method} {response.status_code}', path=request.path[:500], method=request.method, ip_address=ip or None, user_agent=request.META.get('HTTP_USER_AGENT','')[:1000])
        return response
