from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('accounts.urls')),
    path('memberships/', include('memberships.urls')),
    path('activities/', include('activities.urls')),
    path('enterprise/', include('enterprise.urls')),
    path('audit/', include('audit.urls')),
]
