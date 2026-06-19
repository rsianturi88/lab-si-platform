from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from memberships.models import ResearchGroup
import os
class Command(BaseCommand):
    help='Bootstrap superuser and default research groups'
    def handle(self,*args,**opts):
        User=get_user_model()
        username=os.getenv('DJANGO_SUPERUSER_USERNAME','admin')
        email=os.getenv('DJANGO_SUPERUSER_EMAIL','admin@example.com')
        password=os.getenv('DJANGO_SUPERUSER_PASSWORD','ChangeMe123!')
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username,email=email,password=password,role=User.Role.SUPERADMIN,is_verified=True)
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {username}'))
        for name in ['Business Process Management','Digital Governance','Data Analytics','Smart Sustainable IS','Software Engineering']:
            ResearchGroup.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('Bootstrap completed.'))
