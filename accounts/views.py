from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from memberships.models import MemberProfile
from activities.models import LabActivity
from enterprise.models import ResearchProject, CommunityServiceProject, Publication, Partner, CollaborationAgreement, KPIRecord, ProfessionalService, QualityCycleRecord, SOPDocument, WorkPlanBudget, PerformanceReport
from .forms import ProfileForm, SelfMemberProfileForm, AdminUserCreateForm, AdminUserUpdateForm, AdminPasswordResetForm

User = get_user_model()

ADMIN_ROLES = {'SUPERADMIN','LAB_HEAD','ADMIN'}

def is_admin_user(user):
    return user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') in ADMIN_ROLES)

def admin_required(request):
    if not is_admin_user(request.user):
        return HttpResponseForbidden('Akses ditolak. Hanya admin yang dapat mengelola user.')
    return None

@login_required
def dashboard(request):
    stats={
        'Total Anggota': MemberProfile.objects.count(),
        'Anggota Aktif': MemberProfile.objects.filter(status='ACTIVE').count(),
        'Menunggu Verifikasi': MemberProfile.objects.filter(status='PENDING').count(),
        'Kegiatan Lab': LabActivity.objects.count(),
        'Penelitian': ResearchProject.objects.count(),
        'Pengabdian': CommunityServiceProject.objects.count(),
        'Publikasi': Publication.objects.count(),
        'Mitra': Partner.objects.count(),
        'Perjanjian Aktif': CollaborationAgreement.objects.filter(status='ACTIVE').count(),
        'KPI': KPIRecord.objects.count(),
        'Layanan Profesional': ProfessionalService.objects.count(),
        'PPEPP Mutu': QualityCycleRecord.objects.count(),
        'SOP': SOPDocument.objects.count(),
        'RKAT': WorkPlanBudget.objects.count(),
        'Laporan Kinerja': PerformanceReport.objects.count(),
    }
    latest_members=MemberProfile.objects.select_related('user','research_group').order_by('-created_at')[:5]
    latest_activities=LabActivity.objects.order_by('-start_date')[:5]
    latest_research=ResearchProject.objects.select_related('leader').order_by('-created_at')[:5]
    return render(request,'dashboard.html',{'stats':stats,'latest_members':latest_members,'latest_activities':latest_activities,'latest_research':latest_research})

@login_required
def profile(request):
    member, _ = MemberProfile.objects.get_or_create(
        user=request.user,
        defaults={'member_type': MemberProfile.MemberType.LECTURER if request.user.role=='LECTURER' else MemberProfile.MemberType.STUDENT,
                  'status': MemberProfile.Status.ACTIVE if request.user.is_verified else MemberProfile.Status.PENDING}
    )
    user_form=ProfileForm(request.POST or None, instance=request.user, prefix='user')
    member_form=SelfMemberProfileForm(request.POST or None, instance=member, prefix='member')
    if request.method=='POST' and user_form.is_valid() and member_form.is_valid():
        user_form.save()
        mp=member_form.save(commit=False)
        mp.user=request.user
        mp.save(); member_form.save_m2m()
        messages.success(request,'Profil dan informasi keanggotaan berhasil diperbarui.')
        return redirect('profile')
    return render(request,'accounts/profile.html',{'user_form':user_form,'member_form':member_form,'member':member})

@login_required
def user_list(request):
    denied = admin_required(request)
    if denied: return denied
    q=request.GET.get('q','').strip(); role=request.GET.get('role','').strip(); status=request.GET.get('status','').strip()
    qs=User.objects.all().order_by('username')
    if q:
        qs=qs.filter(Q(username__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(email__icontains=q)|Q(institution_id__icontains=q))
    if role:
        qs=qs.filter(role=role)
    if status == 'active':
        qs=qs.filter(is_active=True)
    elif status == 'inactive':
        qs=qs.filter(is_active=False)
    page=Paginator(qs,20).get_page(request.GET.get('page'))
    return render(request,'accounts/user_list.html',{'page':page,'q':q,'role':role,'status':status,'role_choices':User.Role.choices})

@login_required
def user_detail(request, pk):
    denied = admin_required(request)
    if denied: return denied
    obj=get_object_or_404(User, pk=pk)
    member=getattr(obj, 'member_profile', None)
    return render(request,'accounts/user_detail.html',{'obj':obj,'member':member})

@login_required
def user_create(request):
    denied = admin_required(request)
    if denied: return denied
    form=AdminUserCreateForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            cd=form.cleaned_data
            user=form.save(commit=False)
            user.set_password(cd['password'])
            user.save()
            if cd.get('create_member_profile'):
                MemberProfile.objects.create(
                    user=user,
                    member_type=cd.get('member_type') or MemberProfile.MemberType.STUDENT,
                    status=MemberProfile.Status.ACTIVE if user.is_verified else MemberProfile.Status.PENDING,
                    research_group=cd.get('research_group'),
                    expertise=cd.get('expertise',''),
                    program_study=cd.get('program_study',''),
                    generation=cd.get('generation',''),
                    created_by=request.user,
                    updated_by=request.user,
                )
        messages.success(request, f'User {user.username} berhasil dibuat. Password awal: {cd["password"]}')
        return redirect('user_detail', pk=user.pk)
    return render(request,'accounts/user_form.html',{'form':form,'title':'Tambah User Baru','submit_label':'Buat User'})

@login_required
def user_edit(request, pk):
    denied = admin_required(request)
    if denied: return denied
    obj=get_object_or_404(User, pk=pk)
    form=AdminUserUpdateForm(request.POST or None, instance=obj)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request, f'User {obj.username} berhasil diperbarui.')
        return redirect('user_detail', pk=obj.pk)
    return render(request,'accounts/user_form.html',{'form':form,'title':'Edit User','submit_label':'Simpan Perubahan'})

@login_required
def user_password(request, pk):
    denied = admin_required(request)
    if denied: return denied
    obj=get_object_or_404(User, pk=pk)
    form=AdminPasswordResetForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        obj.set_password(form.cleaned_data['password'])
        obj.save(update_fields=['password'])
        messages.success(request, f'Password user {obj.username} berhasil direset.')
        return redirect('user_detail', pk=obj.pk)
    return render(request,'accounts/user_form.html',{'form':form,'title':f'Reset Password: {obj.username}','submit_label':'Reset Password'})

@login_required
def user_delete(request, pk):
    denied = admin_required(request)
    if denied: return denied
    obj=get_object_or_404(User, pk=pk)
    if obj.pk == request.user.pk:
        messages.error(request, 'Admin tidak dapat menghapus akun yang sedang digunakan untuk login.')
        return redirect('user_detail', pk=obj.pk)
    if request.method == 'POST':
        username=obj.username
        obj.delete()
        messages.success(request, f'User {username} dan profil terkait berhasil dihapus.')
        return redirect('user_list')
    return render(request,'confirm_delete.html',{'title':'Hapus User','object_name':obj.username,'cancel_url':'user_detail','cancel_pk':obj.pk})
