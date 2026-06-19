from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Profil Lab", {"fields": ("role","phone","institution_id","is_verified")}),)
    list_display = ('username','email','first_name','last_name','role','institution_id','is_verified','is_staff')
    list_filter = ('role','is_verified','is_staff','is_superuser')
    search_fields = ('username','email','first_name','last_name','institution_id')
