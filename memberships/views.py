from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Q
from .models import MemberProfile, ResearchGroup, MembershipHistory
from .forms import MemberCreateForm, MemberProfileForm, ResearchGroupForm
User=get_user_model()

def require_manager(user): return user.is_authenticated and user.can_manage_members()

@login_required
def member_list(request):
    qs=MemberProfile.objects.select_related('user','research_group').all()
    q=request.GET.get('q','').strip(); status=request.GET.get('status',''); mtype=request.GET.get('type','')
    if q:
        qs=qs.filter(Q(user__first_name__icontains=q)|Q(user__last_name__icontains=q)|Q(user__email__icontains=q)|Q(user__institution_id__icontains=q)|Q(expertise__icontains=q)|Q(program_study__icontains=q)|Q(position__icontains=q))
    if status: qs=qs.filter(status=status)
    if mtype: qs=qs.filter(member_type=mtype)
    page=Paginator(qs,15).get_page(request.GET.get('page'))
    return render(request,'memberships/member_list.html',{'page':page,'q':q,'status':status,'mtype':mtype,'status_choices':MemberProfile.Status.choices,'type_choices':MemberProfile.MemberType.choices})

@login_required
def member_detail(request, pk):
    obj=get_object_or_404(MemberProfile.objects.select_related('user','research_group'),pk=pk)
    return render(request,'memberships/member_detail.html',{'member':obj})

@login_required
def member_create(request):
    if not require_manager(request.user): return HttpResponseForbidden('Akses ditolak.')
    form=MemberCreateForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            cd=form.cleaned_data
            role=User.Role.LECTURER if cd['member_type']=='LECTURER' else User.Role.STUDENT
            u=User.objects.create_user(username=cd['username'],email=cd['email'],password='ChangeMe123!',first_name=cd['first_name'],last_name=cd['last_name'],institution_id=cd['institution_id'],role=role,is_verified=(cd['status']=='ACTIVE'))
            mp=MemberProfile.objects.create(user=u,member_type=cd['member_type'],status=cd['status'],research_group=cd['research_group'],expertise=cd['expertise'],generation=cd['generation'],program_study=cd['program_study'],position=cd['position'],created_by=request.user,updated_by=request.user)
            MembershipHistory.objects.create(member=mp,new_status=cd['status'],changed_by=request.user,reason='Pembuatan anggota awal')
        messages.success(request,'Anggota berhasil dibuat. Password awal: ChangeMe123!')
        return redirect('member_detail', pk=mp.pk)
    return render(request,'memberships/member_form.html',{'form':form,'title':'Tambah Anggota'})

@login_required
def member_edit(request, pk):
    if not require_manager(request.user): return HttpResponseForbidden('Akses ditolak.')
    obj=get_object_or_404(MemberProfile,pk=pk); old_status=obj.status
    form=MemberProfileForm(request.POST or None, instance=obj)
    if request.method=='POST' and form.is_valid():
        mp=form.save(commit=False); mp.updated_by=request.user; mp.save(); form.save_m2m()
        if old_status != mp.status:
            MembershipHistory.objects.create(member=mp,old_status=old_status,new_status=mp.status,changed_by=request.user,reason='Perubahan status melalui form')
        messages.success(request,'Data anggota berhasil diperbarui.'); return redirect('member_detail', pk=mp.pk)
    return render(request,'memberships/member_form.html',{'form':form,'title':'Edit Anggota'})

@login_required
def member_delete(request, pk):
    if not require_manager(request.user): return HttpResponseForbidden('Akses ditolak.')
    obj=get_object_or_404(MemberProfile, pk=pk)
    if obj.user_id == request.user.pk:
        messages.error(request, 'Anda tidak dapat menghapus profil anggota dari akun yang sedang digunakan.')
        return redirect('member_detail', pk=obj.pk)
    if request.method == 'POST':
        name=str(obj)
        obj.user.delete()
        messages.success(request, f'Anggota {name} dan akun terkait berhasil dihapus.')
        return redirect('member_list')
    return render(request,'confirm_delete.html',{'title':'Hapus Anggota','object_name':str(obj),'cancel_url':'member_detail','cancel_pk':obj.pk})

@login_required
def group_list(request):
    groups=ResearchGroup.objects.all().order_by('name')
    return render(request,'memberships/group_list.html',{'groups':groups})

@login_required
def group_detail(request, pk):
    obj=get_object_or_404(ResearchGroup, pk=pk)
    members=obj.memberprofile_set.select_related('user')[:200]
    return render(request,'memberships/group_detail.html',{'group':obj,'members':members})

@login_required
def group_create(request):
    if not require_manager(request.user): return HttpResponseForbidden('Akses ditolak.')
    form=ResearchGroupForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        obj=form.save(); messages.success(request,'Kelompok riset berhasil dibuat.'); return redirect('group_detail', pk=obj.pk)
    return render(request,'memberships/group_form.html',{'form':form,'title':'Tambah Kelompok Riset'})

@login_required
def group_edit(request, pk):
    if not require_manager(request.user): return HttpResponseForbidden('Akses ditolak.')
    obj=get_object_or_404(ResearchGroup, pk=pk)
    form=ResearchGroupForm(request.POST or None, instance=obj)
    if request.method=='POST' and form.is_valid():
        form.save(); messages.success(request,'Kelompok riset berhasil diperbarui.'); return redirect('group_detail', pk=obj.pk)
    return render(request,'memberships/group_form.html',{'form':form,'title':'Edit Kelompok Riset'})

@login_required
def group_delete(request, pk):
    if not require_manager(request.user): return HttpResponseForbidden('Akses ditolak.')
    obj=get_object_or_404(ResearchGroup, pk=pk)
    if request.method == 'POST':
        name=obj.name
        obj.delete()
        messages.success(request, f'Kelompok riset {name} berhasil dihapus.')
        return redirect('group_list')
    return render(request,'confirm_delete.html',{'title':'Hapus Kelompok Riset','object_name':obj.name,'cancel_url':'group_detail','cancel_pk':obj.pk})
