from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import LabActivity
from .forms import LabActivityForm

@login_required
def activity_list(request):
    qs=LabActivity.objects.all()
    q=request.GET.get('q','').strip()
    if q: qs=qs.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(location__icontains=q))
    page=Paginator(qs,12).get_page(request.GET.get('page'))
    return render(request,'activities/activity_list.html',{'page':page,'q':q})

@login_required
def activity_detail(request, pk):
    obj=get_object_or_404(LabActivity,pk=pk)
    return render(request,'activities/activity_detail.html',{'activity':obj})

@login_required
def activity_create(request):
    if not request.user.can_manage_members(): return HttpResponseForbidden('Akses ditolak.')
    form=LabActivityForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        obj=form.save(commit=False); obj.created_by=request.user; obj.save(); form.save_m2m(); messages.success(request,'Kegiatan berhasil dibuat.'); return redirect('activity_detail', pk=obj.pk)
    return render(request,'activities/activity_form.html',{'form':form,'title':'Tambah Kegiatan'})

@login_required
def activity_edit(request, pk):
    if not request.user.can_manage_members(): return HttpResponseForbidden('Akses ditolak.')
    obj=get_object_or_404(LabActivity, pk=pk)
    form=LabActivityForm(request.POST or None, instance=obj)
    if request.method=='POST' and form.is_valid():
        form.save(); messages.success(request,'Kegiatan berhasil diperbarui.'); return redirect('activity_detail', pk=obj.pk)
    return render(request,'activities/activity_form.html',{'form':form,'title':'Edit Kegiatan'})

@login_required
def activity_delete(request, pk):
    if not request.user.can_manage_members(): return HttpResponseForbidden('Akses ditolak.')
    obj=get_object_or_404(LabActivity, pk=pk)
    if request.method == 'POST':
        title=obj.title
        obj.delete()
        messages.success(request, f'Kegiatan {title} berhasil dihapus.')
        return redirect('activity_list')
    return render(request,'confirm_delete.html',{'title':'Hapus Kegiatan','object_name':obj.title,'cancel_url':'activity_detail','cancel_pk':obj.pk})
