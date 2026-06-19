from datetime import date
import math
import re
from collections import Counter, defaultdict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import *
from .forms import *
from memberships.models import MemberProfile, ResearchGroup

MANAGER_ROLES = {'SUPERADMIN','LAB_HEAD','ADMIN','LECTURER'}
ADMIN_ROLES = {'SUPERADMIN','LAB_HEAD','ADMIN'}

def can_manage_enterprise(user):
    return user.is_superuser or getattr(user, 'role', '') in MANAGER_ROLES

def can_admin_crud(user):
    return user.is_superuser or getattr(user, 'role', '') in ADMIN_ROLES

def manager_required(request):
    if not can_manage_enterprise(request.user):
        return HttpResponseForbidden('Akses ditolak. Fitur ini hanya untuk pengelola platform.')
    return None

def paginate(request, qs, per_page=15):
    return Paginator(qs, per_page).get_page(request.GET.get('page'))

def save_form(request, form_class, template, redirect_name, title, instance=None, created_by=False):
    denied = manager_required(request)
    if denied: return denied
    form = form_class(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        if created_by and not obj.pk:
            obj.created_by = request.user
        obj.save(); form.save_m2m()
        messages.success(request, f'{title} berhasil disimpan.')
        if redirect_name.endswith('_detail'):
            return redirect(redirect_name, pk=obj.pk)
        return redirect(redirect_name)
    return render(request, template, {'form':form, 'title':title})

def _display_value(obj, field):
    if field.choices:
        return getattr(obj, f'get_{field.name}_display')()
    val=getattr(obj, field.name)
    if val is None or val == '':
        return '-'
    return val

def render_generic_detail(request, obj, title, edit_url, delete_url, list_url):
    rows=[]
    for f in obj._meta.fields:
        if f.name in {'id'}:
            continue
        rows.append((f.verbose_name.title(), _display_value(obj, f)))
    many=[]
    for f in obj._meta.many_to_many:
        many.append((f.verbose_name.title(), list(getattr(obj, f.name).all()[:100])))
    return render(request,'enterprise/generic_detail.html',{'obj':obj,'title':title,'rows':rows,'many':many,'edit_url':edit_url,'delete_url':delete_url,'list_url':list_url})

def delete_object(request, model, pk, title, redirect_name, detail_url=None):
    denied = manager_required(request)
    if denied: return denied
    obj=get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        label=str(obj)
        obj.delete()
        messages.success(request, f'{title} “{label}” berhasil dihapus.')
        return redirect(redirect_name)
    return render(request,'confirm_delete.html',{'title':f'Hapus {title}','object_name':str(obj),'cancel_url':detail_url or redirect_name,'cancel_pk':obj.pk if detail_url else None})

@login_required
def enterprise_dashboard(request):
    year = int(request.GET.get('year') or date.today().year)
    kpis = KPIRecord.objects.filter(year=year)
    stats = {
        'Penelitian Aktif': ResearchProject.objects.filter(status__in=['FUNDED','ONGOING']).count(),
        'Pengabdian Aktif': CommunityServiceProject.objects.filter(status='ONGOING').count(),
        'Publikasi Tahun Ini': Publication.objects.filter(year=year).count(),
        'Mitra Aktif': Partner.objects.count(),
        'Perjanjian Aktif': CollaborationAgreement.objects.filter(status='ACTIVE').count(),
        'Aset Tersedia': LabAsset.objects.filter(status='AVAILABLE').count(),
        'Total Dana Riset': ResearchProject.objects.aggregate(total=Sum('budget'))['total'] or 0,
        'Layanan Profesional': ProfessionalService.objects.count(),
        'PPEPP Aktif': QualityCycleRecord.objects.filter(status__in=['PLANNED','ONGOING','NEEDS_ACTION']).count(),
        'SOP Disetujui': SOPDocument.objects.filter(status='APPROVED').count(),
        'Praktikum Dikelola': PracticumCourse.objects.count(),
        'Program Talenta': TalentProgram.objects.count(),
        'Laporan Kinerja': PerformanceReport.objects.count(),
    }
    return render(request,'enterprise/dashboard.html',{
        'stats':stats,'year':year,'kpis':kpis,
        'latest_research':ResearchProject.objects.select_related('leader','research_group')[:6],
        'latest_publications':Publication.objects.all()[:6],
        'partner_mix':Partner.objects.values('partner_type').annotate(total=Count('id')).order_by('partner_type'),
    })

@login_required
def research_list(request):
    q=request.GET.get('q','').strip(); status=request.GET.get('status',''); scheme=request.GET.get('scheme','')
    qs=ResearchProject.objects.select_related('leader','research_group','funding_source')
    if q: qs=qs.filter(Q(title__icontains=q)|Q(keywords__icontains=q)|Q(abstract__icontains=q)|Q(expected_outputs__icontains=q))
    if status: qs=qs.filter(status=status)
    if scheme: qs=qs.filter(scheme=scheme)
    return render(request,'enterprise/research_list.html',{'page':paginate(request,qs),'q':q,'status':status,'scheme':scheme,'status_choices':ResearchProject.Status.choices,'scheme_choices':ResearchProject.Scheme.choices})
@login_required
def research_detail(request, pk):
    return render(request,'enterprise/research_detail.html',{'obj':get_object_or_404(ResearchProject.objects.prefetch_related('members','publications','datasets','repositories'),pk=pk)})
@login_required
def research_create(request): return save_form(request, ResearchProjectForm, 'enterprise/form.html', 'research_list', 'Penelitian', created_by=True)
@login_required
def research_edit(request, pk): return save_form(request, ResearchProjectForm, 'enterprise/form.html', 'research_detail', 'Penelitian', get_object_or_404(ResearchProject,pk=pk))
@login_required
def research_delete(request, pk): return delete_object(request, ResearchProject, pk, 'Penelitian', 'research_list', 'research_detail')

@login_required
def service_list(request):
    q=request.GET.get('q','').strip(); qs=CommunityServiceProject.objects.select_related('leader','funding_source')
    if q: qs=qs.filter(Q(title__icontains=q)|Q(partner_name__icontains=q)|Q(output_summary__icontains=q)|Q(outcome_summary__icontains=q))
    return render(request,'enterprise/service_list.html',{'page':paginate(request,qs),'q':q})
@login_required
def service_detail(request, pk): return render(request,'enterprise/service_detail.html',{'obj':get_object_or_404(CommunityServiceProject.objects.prefetch_related('members'),pk=pk)})
@login_required
def service_create(request): return save_form(request, CommunityServiceProjectForm, 'enterprise/form.html', 'service_list', 'Pengabdian', created_by=True)
@login_required
def service_edit(request, pk): return save_form(request, CommunityServiceProjectForm, 'enterprise/form.html', 'service_detail', 'Pengabdian', get_object_or_404(CommunityServiceProject,pk=pk))
@login_required
def service_delete(request, pk): return delete_object(request, CommunityServiceProject, pk, 'Pengabdian', 'service_list', 'service_detail')

@login_required
def publication_list(request):
    q=request.GET.get('q','').strip(); qs=Publication.objects.prefetch_related('authors').select_related('project')
    if q: qs=qs.filter(Q(title__icontains=q)|Q(venue__icontains=q)|Q(doi__icontains=q)|Q(project__title__icontains=q))
    return render(request,'enterprise/publication_list.html',{'page':paginate(request,qs),'q':q})
@login_required
def publication_detail(request, pk): return render_generic_detail(request, get_object_or_404(Publication, pk=pk), 'Detail Publikasi', 'publication_edit', 'publication_delete', 'publication_list')
@login_required
def publication_create(request): return save_form(request, PublicationForm, 'enterprise/form.html', 'publication_list', 'Publikasi')
@login_required
def publication_edit(request, pk): return save_form(request, PublicationForm, 'enterprise/form.html', 'publication_detail', 'Publikasi', get_object_or_404(Publication,pk=pk))
@login_required
def publication_delete(request, pk): return delete_object(request, Publication, pk, 'Publikasi', 'publication_list', 'publication_detail')

@login_required
def partner_list(request):
    q=request.GET.get('q','').strip(); qs=Partner.objects.all().order_by('name')
    if q: qs=qs.filter(Q(name__icontains=q)|Q(contact_person__icontains=q)|Q(email__icontains=q)|Q(strategic_value__icontains=q))
    return render(request,'enterprise/partner_list.html',{'page':paginate(request,qs),'q':q})
@login_required
def partner_detail(request, pk): return render(request,'enterprise/partner_detail.html',{'obj':get_object_or_404(Partner.objects.prefetch_related('agreements'),pk=pk)})
@login_required
def partner_create(request): return save_form(request, PartnerForm, 'enterprise/form.html', 'partner_list', 'Mitra')
@login_required
def partner_edit(request, pk): return save_form(request, PartnerForm, 'enterprise/form.html', 'partner_detail', 'Mitra', get_object_or_404(Partner,pk=pk))
@login_required
def partner_delete(request, pk): return delete_object(request, Partner, pk, 'Mitra', 'partner_list', 'partner_detail')

@login_required
def agreement_list(request):
    q=request.GET.get('q','').strip(); qs=CollaborationAgreement.objects.select_related('partner','owner')
    if q: qs=qs.filter(Q(title__icontains=q)|Q(scope__icontains=q)|Q(partner__name__icontains=q))
    return render(request,'enterprise/agreement_list.html',{'page':paginate(request, qs),'q':q})
@login_required
def agreement_detail(request, pk): return render_generic_detail(request, get_object_or_404(CollaborationAgreement, pk=pk), 'Detail Perjanjian Kerja Sama', 'agreement_edit', 'agreement_delete', 'agreement_list')
@login_required
def agreement_create(request): return save_form(request, CollaborationAgreementForm, 'enterprise/form.html', 'agreement_list', 'Perjanjian Kerja Sama')
@login_required
def agreement_edit(request, pk): return save_form(request, CollaborationAgreementForm, 'enterprise/form.html', 'agreement_detail', 'Perjanjian Kerja Sama', get_object_or_404(CollaborationAgreement,pk=pk))
@login_required
def agreement_delete(request, pk): return delete_object(request, CollaborationAgreement, pk, 'Perjanjian Kerja Sama', 'agreement_list', 'agreement_detail')

@login_required
def dataset_list(request):
    q=request.GET.get('q','').strip(); qs=Dataset.objects.select_related('owner','project').order_by('title')
    if q: qs=qs.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(data_dictionary__icontains=q)|Q(project__title__icontains=q))
    return render(request,'enterprise/dataset_list.html',{'page':paginate(request, qs),'q':q})
@login_required
def dataset_detail(request, pk): return render_generic_detail(request, get_object_or_404(Dataset, pk=pk), 'Detail Dataset', 'dataset_edit', 'dataset_delete', 'dataset_list')
@login_required
def dataset_create(request): return save_form(request, DatasetForm, 'enterprise/form.html', 'dataset_list', 'Dataset')
@login_required
def dataset_edit(request, pk): return save_form(request, DatasetForm, 'enterprise/form.html', 'dataset_detail', 'Dataset', get_object_or_404(Dataset,pk=pk))
@login_required
def dataset_delete(request, pk): return delete_object(request, Dataset, pk, 'Dataset', 'dataset_list', 'dataset_detail')

@login_required
def repository_list(request):
    q=request.GET.get('q','').strip(); qs=SourceCodeRepository.objects.select_related('project').order_by('name')
    if q: qs=qs.filter(Q(name__icontains=q)|Q(technology_stack__icontains=q)|Q(license__icontains=q)|Q(project__title__icontains=q))
    return render(request,'enterprise/repository_list.html',{'page':paginate(request, qs),'q':q})
@login_required
def repository_detail(request, pk): return render_generic_detail(request, get_object_or_404(SourceCodeRepository, pk=pk), 'Detail Repository Source Code', 'repository_edit', 'repository_delete', 'repository_list')
@login_required
def repository_create(request): return save_form(request, SourceCodeRepositoryForm, 'enterprise/form.html', 'repository_list', 'Repositori Kode')
@login_required
def repository_edit(request, pk): return save_form(request, SourceCodeRepositoryForm, 'enterprise/form.html', 'repository_detail', 'Repositori Kode', get_object_or_404(SourceCodeRepository,pk=pk))
@login_required
def repository_delete(request, pk): return delete_object(request, SourceCodeRepository, pk, 'Repositori Kode', 'repository_list', 'repository_detail')

@login_required
def asset_list(request):
    q=request.GET.get('q','').strip(); qs=LabAsset.objects.all().order_by('asset_code')
    if q: qs=qs.filter(Q(asset_code__icontains=q)|Q(name__icontains=q)|Q(category__icontains=q)|Q(location__icontains=q)|Q(notes__icontains=q))
    return render(request,'enterprise/asset_list.html',{'page':paginate(request, qs),'q':q})
@login_required
def asset_detail(request, pk): return render_generic_detail(request, get_object_or_404(LabAsset, pk=pk), 'Detail Aset', 'asset_edit', 'asset_delete', 'asset_list')
@login_required
def asset_create(request): return save_form(request, LabAssetForm, 'enterprise/form.html', 'asset_list', 'Aset')
@login_required
def asset_edit(request, pk): return save_form(request, LabAssetForm, 'enterprise/form.html', 'asset_detail', 'Aset', get_object_or_404(LabAsset,pk=pk))
@login_required
def asset_delete(request, pk): return delete_object(request, LabAsset, pk, 'Aset', 'asset_list', 'asset_detail')

@login_required
def booking_list(request):
    q=request.GET.get('q','').strip(); qs=RoomBooking.objects.select_related('requester','approved_by')
    if q: qs=qs.filter(Q(room_name__icontains=q)|Q(purpose__icontains=q)|Q(requester__user__first_name__icontains=q)|Q(requester__user__last_name__icontains=q))
    return render(request,'enterprise/booking_list.html',{'page':paginate(request, qs),'q':q})
@login_required
def booking_detail(request, pk): return render_generic_detail(request, get_object_or_404(RoomBooking, pk=pk), 'Detail Booking Ruang', 'booking_edit', 'booking_delete', 'booking_list')
@login_required
def booking_create(request): return save_form(request, RoomBookingForm, 'enterprise/form.html', 'booking_list', 'Booking Ruangan')
@login_required
def booking_edit(request, pk): return save_form(request, RoomBookingForm, 'enterprise/form.html', 'booking_detail', 'Booking Ruangan', get_object_or_404(RoomBooking,pk=pk))
@login_required
def booking_delete(request, pk): return delete_object(request, RoomBooking, pk, 'Booking Ruang', 'booking_list', 'booking_detail')

@login_required
def kpi_list(request):
    q=request.GET.get('q','').strip(); qs=KPIRecord.objects.select_related('owner')
    if q: qs=qs.filter(Q(name__icontains=q)|Q(notes__icontains=q)|Q(owner__user__first_name__icontains=q)|Q(owner__user__last_name__icontains=q))
    return render(request,'enterprise/kpi_list.html',{'page':paginate(request, qs, 30),'q':q})
@login_required
def kpi_detail(request, pk): return render_generic_detail(request, get_object_or_404(KPIRecord, pk=pk), 'Detail KPI', 'kpi_edit', 'kpi_delete', 'kpi_list')
@login_required
def kpi_create(request): return save_form(request, KPIRecordForm, 'enterprise/form.html', 'kpi_list', 'KPI')
@login_required
def kpi_edit(request, pk): return save_form(request, KPIRecordForm, 'enterprise/form.html', 'kpi_detail', 'KPI', get_object_or_404(KPIRecord,pk=pk))
@login_required
def kpi_delete(request, pk): return delete_object(request, KPIRecord, pk, 'KPI', 'kpi_list', 'kpi_detail')

@login_required
def organization_list(request):
    return render(request,'enterprise/organization_list.html',{'units':OrganizationUnit.objects.all(),'positions':LabPosition.objects.select_related('member','unit')})
@login_required
def organization_detail(request, pk): return render_generic_detail(request, get_object_or_404(OrganizationUnit, pk=pk), 'Detail Unit Organisasi', 'organization_edit', 'organization_delete', 'organization_list')
@login_required
def organization_create(request): return save_form(request, OrganizationUnitForm, 'enterprise/form.html', 'organization_list', 'Unit Organisasi')
@login_required
def organization_edit(request, pk): return save_form(request, OrganizationUnitForm, 'enterprise/form.html', 'organization_detail', 'Unit Organisasi', get_object_or_404(OrganizationUnit, pk=pk))
@login_required
def organization_delete(request, pk): return delete_object(request, OrganizationUnit, pk, 'Unit Organisasi', 'organization_list', 'organization_detail')
@login_required
def position_create(request): return save_form(request, LabPositionForm, 'enterprise/form.html', 'organization_list', 'Jabatan Laboratorium')
@login_required
def position_detail(request, pk): return render_generic_detail(request, get_object_or_404(LabPosition, pk=pk), 'Detail Jabatan Laboratorium', 'position_edit', 'position_delete', 'organization_list')
@login_required
def position_edit(request, pk): return save_form(request, LabPositionForm, 'enterprise/form.html', 'position_detail', 'Jabatan Laboratorium', get_object_or_404(LabPosition, pk=pk))
@login_required
def position_delete(request, pk): return delete_object(request, LabPosition, pk, 'Jabatan Laboratorium', 'organization_list', 'position_detail')


# Head of Laboratory governance and service modules

def _safe_display(obj, attr):
    if callable(attr):
        val = attr(obj)
    else:
        if attr.endswith('_display'):
            field = attr[:-8]
            val = getattr(obj, f'get_{field}_display')()
        else:
            val = getattr(obj, attr, '-')
    if val is None or val == '':
        return '-'
    return val

def render_simple_list(request, model, template_title, create_url, detail_url, edit_url, delete_url, search_fields, columns, qs=None, extra_filters=None, per_page=20):
    q=request.GET.get('q','').strip()
    qs = qs if qs is not None else model.objects.all()
    if q and search_fields:
        query = Q()
        for field in search_fields:
            query |= Q(**{f'{field}__icontains': q})
        qs = qs.filter(query)
    rows=[]
    for obj in paginate(request, qs, per_page):
        rows.append({'obj':obj,'cells':[(label, _safe_display(obj, attr)) for label, attr in columns]})
    page=paginate(request, qs, per_page)
    rows=[]
    for obj in page:
        rows.append({'obj':obj,'cells':[(label, _safe_display(obj, attr)) for label, attr in columns]})
    return render(request,'enterprise/simple_list.html',{
        'title':template_title,'page':page,'rows':rows,'q':q,'create_url':create_url,'detail_url':detail_url,'edit_url':edit_url,'delete_url':delete_url,'extra_filters':extra_filters or []
    })

@login_required
def professional_service_list(request):
    qs=ProfessionalService.objects.select_related('coordinator','partner')
    return render_simple_list(request, ProfessionalService, 'Layanan Profesional', 'professional_service_create', 'professional_service_detail', 'professional_service_edit', 'professional_service_delete', ['title','description','requester_organization','requester_name','coordinator__user__first_name','coordinator__user__last_name'], [('Layanan','title'),('Tipe','service_type_display'),('Audiens','audience_display'),('Skema','pricing_display'),('Status','status_display'),('Koordinator','coordinator'),('Mitra/Instansi','requester_organization')], qs)
@login_required
def professional_service_detail(request, pk): return render_generic_detail(request, get_object_or_404(ProfessionalService, pk=pk), 'Detail Layanan Profesional', 'professional_service_edit', 'professional_service_delete', 'professional_service_list')
@login_required
def professional_service_create(request): return save_form(request, ProfessionalServiceForm, 'enterprise/form.html', 'professional_service_list', 'Layanan Profesional', created_by=True)
@login_required
def professional_service_edit(request, pk): return save_form(request, ProfessionalServiceForm, 'enterprise/form.html', 'professional_service_detail', 'Layanan Profesional', get_object_or_404(ProfessionalService,pk=pk))
@login_required
def professional_service_delete(request, pk): return delete_object(request, ProfessionalService, pk, 'Layanan Profesional', 'professional_service_list', 'professional_service_detail')

@login_required
def quality_cycle_list(request):
    qs=QualityCycleRecord.objects.select_related('owner')
    return render_simple_list(request, QualityCycleRecord, 'Siklus PPEPP Mutu', 'quality_cycle_create', 'quality_cycle_detail', 'quality_cycle_edit', 'quality_cycle_delete', ['title','period','standard','implementation_summary','evaluation_findings','corrective_action'], [('Judul','title'),('Domain','domain_display'),('Tahap','stage_display'),('Periode','period'),('Status','status_display'),('PIC','owner')], qs)
@login_required
def quality_cycle_detail(request, pk): return render_generic_detail(request, get_object_or_404(QualityCycleRecord, pk=pk), 'Detail PPEPP Mutu', 'quality_cycle_edit', 'quality_cycle_delete', 'quality_cycle_list')
@login_required
def quality_cycle_create(request): return save_form(request, QualityCycleRecordForm, 'enterprise/form.html', 'quality_cycle_list', 'PPEPP Mutu')
@login_required
def quality_cycle_edit(request, pk): return save_form(request, QualityCycleRecordForm, 'enterprise/form.html', 'quality_cycle_detail', 'PPEPP Mutu', get_object_or_404(QualityCycleRecord,pk=pk))
@login_required
def quality_cycle_delete(request, pk): return delete_object(request, QualityCycleRecord, pk, 'PPEPP Mutu', 'quality_cycle_list', 'quality_cycle_detail')

@login_required
def workplan_list(request):
    qs=WorkPlanBudget.objects.select_related('funding_source','owner')
    return render_simple_list(request, WorkPlanBudget, 'Rencana Kerja dan Anggaran Tahunan', 'workplan_create', 'workplan_detail', 'workplan_edit', 'workplan_delete', ['program_name','notes','year'], [('Tahun','year'),('Program','program_name'),('Area','area_display'),('Anggaran','budget'),('Realisasi','realization'),('Serapan %','absorption_percent'),('Status','status_display')], qs)
@login_required
def workplan_detail(request, pk): return render_generic_detail(request, get_object_or_404(WorkPlanBudget, pk=pk), 'Detail RKAT', 'workplan_edit', 'workplan_delete', 'workplan_list')
@login_required
def workplan_create(request): return save_form(request, WorkPlanBudgetForm, 'enterprise/form.html', 'workplan_list', 'RKAT')
@login_required
def workplan_edit(request, pk): return save_form(request, WorkPlanBudgetForm, 'enterprise/form.html', 'workplan_detail', 'RKAT', get_object_or_404(WorkPlanBudget,pk=pk))
@login_required
def workplan_delete(request, pk): return delete_object(request, WorkPlanBudget, pk, 'RKAT', 'workplan_list', 'workplan_detail')

@login_required
def sop_list(request):
    qs=SOPDocument.objects.select_related('owner')
    return render_simple_list(request, SOPDocument, 'SOP dan Tata Laksana', 'sop_create', 'sop_detail', 'sop_edit', 'sop_delete', ['code','title','description'], [('Kode','code'),('Judul','title'),('Area','area_display'),('Versi','version'),('Status','status_display'),('Tanggal Berlaku','effective_date')], qs)
@login_required
def sop_detail(request, pk): return render_generic_detail(request, get_object_or_404(SOPDocument, pk=pk), 'Detail SOP', 'sop_edit', 'sop_delete', 'sop_list')
@login_required
def sop_create(request): return save_form(request, SOPDocumentForm, 'enterprise/form.html', 'sop_list', 'SOP')
@login_required
def sop_edit(request, pk): return save_form(request, SOPDocumentForm, 'enterprise/form.html', 'sop_detail', 'SOP', get_object_or_404(SOPDocument,pk=pk))
@login_required
def sop_delete(request, pk): return delete_object(request, SOPDocument, pk, 'SOP', 'sop_list', 'sop_detail')

@login_required
def practicum_list(request):
    qs=PracticumCourse.objects.select_related('coordinator')
    return render_simple_list(request, PracticumCourse, 'Manajemen Praktikum', 'practicum_create', 'practicum_detail', 'practicum_edit', 'practicum_delete', ['course_code','course_name','study_program','academic_year','implementation_notes','evaluation_summary'], [('Kode','course_code'),('Mata Kuliah','course_name'),('Prodi','study_program'),('Tahun Akademik','academic_year'),('Koordinator','coordinator'),('Modul','module_status_display')], qs)
@login_required
def practicum_detail(request, pk): return render_generic_detail(request, get_object_or_404(PracticumCourse, pk=pk), 'Detail Praktikum', 'practicum_edit', 'practicum_delete', 'practicum_list')
@login_required
def practicum_create(request): return save_form(request, PracticumCourseForm, 'enterprise/form.html', 'practicum_list', 'Praktikum')
@login_required
def practicum_edit(request, pk): return save_form(request, PracticumCourseForm, 'enterprise/form.html', 'practicum_detail', 'Praktikum', get_object_or_404(PracticumCourse,pk=pk))
@login_required
def practicum_delete(request, pk): return delete_object(request, PracticumCourse, pk, 'Praktikum', 'practicum_list', 'practicum_detail')

@login_required
def curriculum_support_list(request):
    qs=CurriculumSupport.objects.select_related('owner')
    return render_simple_list(request, CurriculumSupport, 'Dukungan Kurikulum', 'curriculum_support_create', 'curriculum_support_detail', 'curriculum_support_edit', 'curriculum_support_delete', ['study_program','course_name','recommendation'], [('Prodi','study_program'),('Tahun Kurikulum','curriculum_year'),('Mata Kuliah','course_name'),('Kontribusi','contribution_type_display'),('Status','status_display'),('PIC','owner')], qs)
@login_required
def curriculum_support_detail(request, pk): return render_generic_detail(request, get_object_or_404(CurriculumSupport, pk=pk), 'Detail Dukungan Kurikulum', 'curriculum_support_edit', 'curriculum_support_delete', 'curriculum_support_list')
@login_required
def curriculum_support_create(request): return save_form(request, CurriculumSupportForm, 'enterprise/form.html', 'curriculum_support_list', 'Dukungan Kurikulum')
@login_required
def curriculum_support_edit(request, pk): return save_form(request, CurriculumSupportForm, 'enterprise/form.html', 'curriculum_support_detail', 'Dukungan Kurikulum', get_object_or_404(CurriculumSupport,pk=pk))
@login_required
def curriculum_support_delete(request, pk): return delete_object(request, CurriculumSupport, pk, 'Dukungan Kurikulum', 'curriculum_support_list', 'curriculum_support_detail')

@login_required
def roadmap_list(request):
    qs=RoadmapItem.objects.select_related('owner','owner_group')
    return render_simple_list(request, RoadmapItem, 'Roadmap Riset, Inovasi, dan Pengabdian', 'roadmap_create', 'roadmap_detail', 'roadmap_edit', 'roadmap_delete', ['title','theme','alignment_policy','expected_outputs'], [('Judul','title'),('Area','area_display'),('Tema','theme'),('Periode', lambda o: f'{o.start_year}-{o.end_year}'),('Prioritas','priority_display'),('Status','status_display'),('Grup','owner_group')], qs)
@login_required
def roadmap_detail(request, pk): return render_generic_detail(request, get_object_or_404(RoadmapItem, pk=pk), 'Detail Roadmap', 'roadmap_edit', 'roadmap_delete', 'roadmap_list')
@login_required
def roadmap_create(request): return save_form(request, RoadmapItemForm, 'enterprise/form.html', 'roadmap_list', 'Roadmap')
@login_required
def roadmap_edit(request, pk): return save_form(request, RoadmapItemForm, 'enterprise/form.html', 'roadmap_detail', 'Roadmap', get_object_or_404(RoadmapItem,pk=pk))
@login_required
def roadmap_delete(request, pk): return delete_object(request, RoadmapItem, pk, 'Roadmap', 'roadmap_list', 'roadmap_detail')

@login_required
def talent_program_list(request):
    qs=TalentProgram.objects.select_related('coordinator')
    return render_simple_list(request, TalentProgram, 'Rekrutmen dan Pembinaan Talenta', 'talent_program_create', 'talent_program_detail', 'talent_program_edit', 'talent_program_delete', ['title','period','selection_criteria','mentoring_plan','result_summary'], [('Program','title'),('Tipe','program_type_display'),('Periode','period'),('Status','status_display'),('Koordinator','coordinator')], qs)
@login_required
def talent_program_detail(request, pk): return render_generic_detail(request, get_object_or_404(TalentProgram, pk=pk), 'Detail Program Talenta', 'talent_program_edit', 'talent_program_delete', 'talent_program_list')
@login_required
def talent_program_create(request): return save_form(request, TalentProgramForm, 'enterprise/form.html', 'talent_program_list', 'Program Talenta')
@login_required
def talent_program_edit(request, pk): return save_form(request, TalentProgramForm, 'enterprise/form.html', 'talent_program_detail', 'Program Talenta', get_object_or_404(TalentProgram,pk=pk))
@login_required
def talent_program_delete(request, pk): return delete_object(request, TalentProgram, pk, 'Program Talenta', 'talent_program_list', 'talent_program_detail')

@login_required
def digital_channel_list(request):
    qs=DigitalChannel.objects.select_related('owner')
    return render_simple_list(request, DigitalChannel, 'Kanal Komunikasi Digital', 'digital_channel_create', 'digital_channel_detail', 'digital_channel_edit', 'digital_channel_delete', ['name','url','audience','content_strategy','performance_notes'], [('Kanal','name'),('Tipe','channel_type_display'),('Audiens','audience'),('Status','status_display'),('Update Terakhir','last_update'),('PIC','owner')], qs)
@login_required
def digital_channel_detail(request, pk): return render_generic_detail(request, get_object_or_404(DigitalChannel, pk=pk), 'Detail Kanal Digital', 'digital_channel_edit', 'digital_channel_delete', 'digital_channel_list')
@login_required
def digital_channel_create(request): return save_form(request, DigitalChannelForm, 'enterprise/form.html', 'digital_channel_list', 'Kanal Digital')
@login_required
def digital_channel_edit(request, pk): return save_form(request, DigitalChannelForm, 'enterprise/form.html', 'digital_channel_detail', 'Kanal Digital', get_object_or_404(DigitalChannel,pk=pk))
@login_required
def digital_channel_delete(request, pk): return delete_object(request, DigitalChannel, pk, 'Kanal Digital', 'digital_channel_list', 'digital_channel_detail')

@login_required
def satisfaction_survey_list(request):
    qs=SatisfactionSurvey.objects.select_related('owner')
    return render_simple_list(request, SatisfactionSurvey, 'Monitoring Kepuasan Pengguna', 'satisfaction_survey_create', 'satisfaction_survey_detail', 'satisfaction_survey_edit', 'satisfaction_survey_delete', ['period','respondent_segment','summary','follow_up'], [('Domain','domain_display'),('Periode','period'),('Responden','respondent_segment'),('Skor','score'),('Sampel','sample_size'),('Tindak Lanjut','follow_up')], qs)
@login_required
def satisfaction_survey_detail(request, pk): return render_generic_detail(request, get_object_or_404(SatisfactionSurvey, pk=pk), 'Detail Kepuasan Pengguna', 'satisfaction_survey_edit', 'satisfaction_survey_delete', 'satisfaction_survey_list')
@login_required
def satisfaction_survey_create(request): return save_form(request, SatisfactionSurveyForm, 'enterprise/form.html', 'satisfaction_survey_list', 'Monitoring Kepuasan')
@login_required
def satisfaction_survey_edit(request, pk): return save_form(request, SatisfactionSurveyForm, 'enterprise/form.html', 'satisfaction_survey_detail', 'Monitoring Kepuasan', get_object_or_404(SatisfactionSurvey,pk=pk))
@login_required
def satisfaction_survey_delete(request, pk): return delete_object(request, SatisfactionSurvey, pk, 'Monitoring Kepuasan', 'satisfaction_survey_list', 'satisfaction_survey_detail')

@login_required
def performance_report_list(request):
    qs=PerformanceReport.objects.select_related('prepared_by','approved_by')
    return render_simple_list(request, PerformanceReport, 'Laporan Kinerja Laboratorium', 'performance_report_create', 'performance_report_detail', 'performance_report_edit', 'performance_report_delete', ['title','executive_summary','year'], [('Tahun','year'),('Judul','title'),('Tipe','report_type_display'),('Status','status_display'),('Penyusun','prepared_by'),('Disampaikan','submitted_at')], qs)
@login_required
def performance_report_detail(request, pk): return render_generic_detail(request, get_object_or_404(PerformanceReport, pk=pk), 'Detail Laporan Kinerja', 'performance_report_edit', 'performance_report_delete', 'performance_report_list')
@login_required
def performance_report_create(request): return save_form(request, PerformanceReportForm, 'enterprise/form.html', 'performance_report_list', 'Laporan Kinerja')
@login_required
def performance_report_edit(request, pk): return save_form(request, PerformanceReportForm, 'enterprise/form.html', 'performance_report_detail', 'Laporan Kinerja', get_object_or_404(PerformanceReport,pk=pk))
@login_required
def performance_report_delete(request, pk): return delete_object(request, PerformanceReport, pk, 'Laporan Kinerja', 'performance_report_list', 'performance_report_detail')

@login_required
def head_approval_list(request):
    qs=HeadApproval.objects.select_related('requester','approver')
    return render_simple_list(request, HeadApproval, 'Otorisasi Kepala Laboratorium', 'head_approval_create', 'head_approval_detail', 'head_approval_edit', 'head_approval_delete', ['title','subject_reference','rationale','decision_notes'], [('Judul','title'),('Jenis','decision_type_display'),('Status','status_display'),('Pemohon','requester'),('Approver','approver'),('Diputuskan','decided_at')], qs)
@login_required
def head_approval_detail(request, pk): return render_generic_detail(request, get_object_or_404(HeadApproval, pk=pk), 'Detail Otorisasi Kepala Lab', 'head_approval_edit', 'head_approval_delete', 'head_approval_list')
@login_required
def head_approval_create(request): return save_form(request, HeadApprovalForm, 'enterprise/form.html', 'head_approval_list', 'Otorisasi Kepala Lab')
@login_required
def head_approval_edit(request, pk): return save_form(request, HeadApprovalForm, 'enterprise/form.html', 'head_approval_detail', 'Otorisasi Kepala Lab', get_object_or_404(HeadApproval,pk=pk))
@login_required
def head_approval_delete(request, pk): return delete_object(request, HeadApproval, pk, 'Otorisasi Kepala Lab', 'head_approval_list', 'head_approval_detail')

# Knowledge graph search/retrieval

def _add_node(nodes, node_id, label, ntype, meta=None, url=None):
    if node_id not in nodes:
        nodes[node_id]={'data':{'id':node_id,'label':str(label)[:90], 'type':ntype, 'meta':str(meta or '')[:300], 'url':url or ''}}

def _add_edge(edges, source, target, label):
    edge_id=f'{source}_{target}_{label}'
    edges[edge_id]={'data':{'id':edge_id,'source':source,'target':target,'label':label}}

def _matches_text(q, *vals):
    if not q: return False
    q=q.lower()
    return any(q in str(v or '').lower() for v in vals)

def _member_url(pk): return reverse('member_detail', args=[pk])
def _research_url(pk): return reverse('research_detail', args=[pk])
def _service_url(pk): return reverse('service_detail', args=[pk])
def _partner_url(pk): return reverse('partner_detail', args=[pk])
def _professional_service_url(pk): return reverse('professional_service_detail', args=[pk])

def _graph_for_query(q, entity_type=''):
    nodes, edges = {}, {}
    if not q:
        return [], {'nodes':0,'edges':0,'message':'Masukkan kata kunci untuk menampilkan knowledge graph kontekstual.'}
    q=q.strip()
    wanted = entity_type or 'ALL'
    matched_count=0
    limit=80

    def add_group(g):
        _add_node(nodes, f'g{g.id}', g.name, 'Research Group', g.description)

    def add_member(m):
        _add_node(nodes, f'm{m.id}', str(m), 'Member', f'{m.get_member_type_display()} | {m.expertise} | {m.program_study}', _member_url(m.pk))
        if m.research_group_id:
            add_group(m.research_group); _add_edge(edges, f'm{m.id}', f'g{m.research_group_id}', 'anggota')

    def add_research(r):
        _add_node(nodes, f'r{r.id}', r.title, 'Research', f'{r.get_status_display()} | {r.keywords}', _research_url(r.pk))
        if r.research_group_id:
            add_group(r.research_group); _add_edge(edges, f'g{r.research_group_id}', f'r{r.id}', 'membawahi')
        if r.leader_id:
            add_member(r.leader); _add_edge(edges, f'm{r.leader_id}', f'r{r.id}', 'memimpin')
        for m in r.members.select_related('user','research_group')[:12]:
            add_member(m); _add_edge(edges, f'm{m.id}', f'r{r.id}', 'berkontribusi')

    def add_service(s):
        _add_node(nodes, f's{s.id}', s.title, 'Service', f'{s.get_status_display()} | {s.partner_name}', _service_url(s.pk))
        if s.leader_id:
            add_member(s.leader); _add_edge(edges, f'm{s.leader_id}', f's{s.id}', 'memimpin')

    def add_publication(pub):
        _add_node(nodes, f'pub{pub.id}', pub.title, 'Publication', f'{pub.get_indexing_display()} | {pub.venue} | {pub.year}', reverse('publication_detail', args=[pub.pk]))
        if pub.project_id:
            add_research(pub.project); _add_edge(edges, f'r{pub.project_id}', f'pub{pub.id}', 'menghasilkan')
        for author in pub.authors.select_related('user','research_group')[:12]:
            add_member(author); _add_edge(edges, f'm{author.id}', f'pub{pub.id}', 'menulis')

    def add_dataset(d):
        _add_node(nodes, f'd{d.id}', d.title, 'Dataset', f'{d.access_level} | versi {d.version}', reverse('dataset_detail', args=[d.pk]))
        if d.project_id: add_research(d.project); _add_edge(edges, f'r{d.project_id}', f'd{d.id}', 'memiliki data')
        if d.owner_id: add_member(d.owner); _add_edge(edges, f'm{d.owner_id}', f'd{d.id}', 'mengelola')

    def add_repo(repo):
        _add_node(nodes, f'code{repo.id}', repo.name, 'Repository', repo.technology_stack, reverse('repository_detail', args=[repo.pk]))
        if repo.project_id: add_research(repo.project); _add_edge(edges, f'r{repo.project_id}', f'code{repo.id}', 'menghasilkan kode')

    def add_partner(p):
        _add_node(nodes, f'p{p.id}', p.name, 'Partner', p.get_partner_type_display(), _partner_url(p.pk))
        for a in p.agreements.select_related('owner')[:10]:
            add_agreement(a)

    def add_agreement(a):
        _add_node(nodes, f'a{a.id}', a.title, 'Agreement', f'{a.get_agreement_type_display()} | {a.get_status_display()}', reverse('agreement_detail', args=[a.pk]))
        if a.partner_id:
            _add_node(nodes, f'p{a.partner_id}', a.partner.name, 'Partner', a.partner.get_partner_type_display(), _partner_url(a.partner_id)); _add_edge(edges, f'p{a.partner_id}', f'a{a.id}', 'terikat')
        if a.owner_id:
            add_member(a.owner); _add_edge(edges, f'm{a.owner_id}', f'a{a.id}', 'PIC')


    def add_professional_service(s):
        _add_node(nodes, f'ps{s.id}', s.title, 'Layanan Profesional', f'{s.get_service_type_display()} | {s.get_pricing_display()} | {s.get_status_display()} | {s.requester_organization}', _professional_service_url(s.pk))
        if s.coordinator_id:
            add_member(s.coordinator); _add_edge(edges, f'm{s.coordinator_id}', f'ps{s.id}', 'koordinator')
        if s.partner_id:
            _add_node(nodes, f'p{s.partner_id}', s.partner.name, 'Partner', s.partner.get_partner_type_display(), _partner_url(s.partner_id)); _add_edge(edges, f'p{s.partner_id}', f'ps{s.id}', 'menggunakan layanan')
        for expert in s.experts.select_related('user','research_group')[:12]:
            add_member(expert); _add_edge(edges, f'm{expert.id}', f'ps{s.id}', 'pakar')

    def add_sop_doc(sop):
        _add_node(nodes, f'sop{sop.id}', sop.title, 'SOP', f'{sop.code} | {sop.get_area_display()} | {sop.get_status_display()}', reverse('sop_detail', args=[sop.pk]))
        if sop.owner_id:
            add_member(sop.owner); _add_edge(edges, f'm{sop.owner_id}', f'sop{sop.id}', 'owner')

    def add_roadmap_item(rm):
        _add_node(nodes, f'road{rm.id}', rm.title, 'Roadmap', f'{rm.get_area_display()} | {rm.theme} | {rm.start_year}-{rm.end_year}', reverse('roadmap_detail', args=[rm.pk]))
        if rm.owner_group_id:
            add_group(rm.owner_group); _add_edge(edges, f'g{rm.owner_group_id}', f'road{rm.id}', 'menjalankan')
        if rm.owner_id:
            add_member(rm.owner); _add_edge(edges, f'm{rm.owner_id}', f'road{rm.id}', 'PIC')

    def add_quality_cycle(qc):
        _add_node(nodes, f'q{qc.id}', qc.title, 'PPEPP', f'{qc.get_domain_display()} | {qc.get_stage_display()} | {qc.period}', reverse('quality_cycle_detail', args=[qc.pk]))
        if qc.owner_id:
            add_member(qc.owner); _add_edge(edges, f'm{qc.owner_id}', f'q{qc.id}', 'PIC mutu')

    def add_if(kind, qs, add_fn):
        nonlocal matched_count
        if wanted not in {'ALL', kind}: return
        for obj in qs[:limit]:
            add_fn(obj); matched_count += 1

    add_if('GROUP', ResearchGroup.objects.filter(Q(name__icontains=q)|Q(description__icontains=q)), add_group)
    add_if('MEMBER', MemberProfile.objects.select_related('user','research_group').filter(Q(user__first_name__icontains=q)|Q(user__last_name__icontains=q)|Q(user__email__icontains=q)|Q(user__institution_id__icontains=q)|Q(expertise__icontains=q)|Q(program_study__icontains=q)|Q(position__icontains=q)), add_member)
    add_if('RESEARCH', ResearchProject.objects.select_related('research_group','leader','funding_source').prefetch_related('members').filter(Q(title__icontains=q)|Q(abstract__icontains=q)|Q(keywords__icontains=q)|Q(expected_outputs__icontains=q)), add_research)
    add_if('SERVICE', CommunityServiceProject.objects.select_related('leader').filter(Q(title__icontains=q)|Q(partner_name__icontains=q)|Q(output_summary__icontains=q)|Q(outcome_summary__icontains=q)), add_service)
    add_if('PUBLICATION', Publication.objects.select_related('project').prefetch_related('authors').filter(Q(title__icontains=q)|Q(venue__icontains=q)|Q(doi__icontains=q)|Q(project__title__icontains=q)), add_publication)
    add_if('DATASET', Dataset.objects.select_related('owner','project').filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(data_dictionary__icontains=q)|Q(project__title__icontains=q)), add_dataset)
    add_if('REPOSITORY', SourceCodeRepository.objects.select_related('project').filter(Q(name__icontains=q)|Q(technology_stack__icontains=q)|Q(project__title__icontains=q)), add_repo)
    add_if('PARTNER', Partner.objects.prefetch_related('agreements').filter(Q(name__icontains=q)|Q(strategic_value__icontains=q)|Q(contact_person__icontains=q)|Q(email__icontains=q)), add_partner)
    add_if('AGREEMENT', CollaborationAgreement.objects.select_related('partner','owner').filter(Q(title__icontains=q)|Q(scope__icontains=q)|Q(partner__name__icontains=q)), add_agreement)
    add_if('PROF_SERVICE', ProfessionalService.objects.select_related('coordinator','partner').prefetch_related('experts').filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(deliverables__icontains=q)|Q(requester_organization__icontains=q)|Q(requester_name__icontains=q)), add_professional_service)
    add_if('SOP', SOPDocument.objects.select_related('owner').filter(Q(code__icontains=q)|Q(title__icontains=q)|Q(description__icontains=q)), add_sop_doc)
    add_if('ROADMAP', RoadmapItem.objects.select_related('owner','owner_group').filter(Q(title__icontains=q)|Q(theme__icontains=q)|Q(alignment_policy__icontains=q)|Q(expected_outputs__icontains=q)), add_roadmap_item)
    add_if('PPEPP', QualityCycleRecord.objects.select_related('owner').filter(Q(title__icontains=q)|Q(period__icontains=q)|Q(standard__icontains=q)|Q(evaluation_findings__icontains=q)|Q(corrective_action__icontains=q)), add_quality_cycle)

    elements=list(nodes.values())+list(edges.values())
    return elements, {'nodes':len(nodes),'edges':len(edges),'matched':matched_count,'message':'' if elements else 'Tidak ditemukan node yang sesuai dengan kata kunci.'}

@login_required
def knowledge_graph(request):
    q=request.GET.get('q','').strip()
    entity_type=request.GET.get('type','').strip()
    elements, graph_stats = _graph_for_query(q, entity_type)
    summary={
        **graph_stats,
        'indexed': MemberProfile.objects.count()+ResearchProject.objects.count()+CommunityServiceProject.objects.count()+Publication.objects.count()+Partner.objects.count()+CollaborationAgreement.objects.count()+Dataset.objects.count()+SourceCodeRepository.objects.count()+ResearchGroup.objects.count()+ProfessionalService.objects.count()+SOPDocument.objects.count()+RoadmapItem.objects.count()+QualityCycleRecord.objects.count(),
        'research':ResearchProject.objects.count(),
        'publications':Publication.objects.count(),
        'partners':Partner.objects.count(),
    }
    type_choices=[('','Semua Entitas'),('GROUP','Kelompok Riset'),('MEMBER','Anggota'),('RESEARCH','Penelitian'),('SERVICE','Pengabdian'),('PROF_SERVICE','Layanan Profesional'),('PUBLICATION','Publikasi'),('DATASET','Dataset'),('REPOSITORY','Source Code'),('PARTNER','Mitra'),('AGREEMENT','Perjanjian'),('SOP','SOP'),('ROADMAP','Roadmap'),('PPEPP','PPEPP')]
    examples=['Business Process Management','AI','Digital Government','Pelatihan','Konsultasi','SOP','PPEPP','RKAT','Asisten Praktikum','Laporan Kinerja']
    return render(request,'enterprise/knowledge_graph.html',{'elements':elements,'summary':summary,'q':q,'entity_type':entity_type,'type_choices':type_choices,'examples':examples})

# Local RAG chatbot
STOPWORDS={'yang','dan','atau','untuk','dengan','dari','pada','adalah','apa','siapa','bagaimana','mana','saja','di','ke','ini','itu','dalam','the','and','of','a','an','to','for','is','are'}

def _tokenize(text):
    return [t for t in re.findall(r'[a-zA-Z0-9_\-]+', (text or '').lower()) if len(t)>2 and t not in STOPWORDS]

def _rag_corpus():
    docs=[]
    def add(kind, title, text, url='', meta=''):
        full=f'{title} {text} {meta}'
        docs.append({'kind':kind,'title':str(title),'text':str(text or ''),'url':url,'meta':meta,'tokens':_tokenize(full)})
    for m in MemberProfile.objects.select_related('user','research_group')[:800]:
        add('Anggota', str(m), f"Email {m.user.email}. ID {m.user.institution_id}. Tipe {m.get_member_type_display()}. Status {m.get_status_display()}. Kelompok riset {m.research_group or '-'}. Keahlian {m.expertise}. Program studi {m.program_study}. Posisi {m.position}. Catatan {m.notes}", _member_url(m.pk))
    for g in ResearchGroup.objects.all()[:300]: add('Kelompok Riset', g.name, g.description, reverse('group_detail', args=[g.pk]))
    for r in ResearchProject.objects.select_related('leader','research_group','funding_source')[:800]: add('Penelitian', r.title, f"Abstrak {r.abstract}. Status {r.get_status_display()}. Skema {r.get_scheme_display()}. Ketua {r.leader}. Grup {r.research_group}. Dana {r.budget}. Kata kunci {r.keywords}. Output {r.expected_outputs}. Risiko {r.risks}", _research_url(r.pk))
    for s in CommunityServiceProject.objects.select_related('leader','funding_source')[:500]: add('Pengabdian', s.title, f"Mitra {s.partner_name}. Status {s.get_status_display()}. Ketua {s.leader}. Dana {s.budget}. Output {s.output_summary}. Outcome {s.outcome_summary}", _service_url(s.pk))
    for p in Publication.objects.select_related('project')[:800]: add('Publikasi', p.title, f"Tipe {p.get_publication_type_display()}. Indeks {p.get_indexing_display()}. Venue {p.venue}. Tahun {p.year}. DOI {p.doi}. Sitasi {p.citation_count}. Proyek {p.project}", reverse('publication_detail', args=[p.pk]))
    for p in Partner.objects.all()[:500]: add('Mitra', p.name, f"Tipe {p.get_partner_type_display()}. Kontak {p.contact_person}. Email {p.email}. Telepon {p.phone}. Alamat {p.address}. Nilai strategis {p.strategic_value}", _partner_url(p.pk))
    for a in CollaborationAgreement.objects.select_related('partner','owner')[:500]: add('Perjanjian', a.title, f"Tipe {a.get_agreement_type_display()}. Status {a.get_status_display()}. Mitra {a.partner}. Mulai {a.start_date}. Akhir {a.end_date}. Lingkup {a.scope}. PIC {a.owner}", reverse('agreement_detail', args=[a.pk]))
    for d in Dataset.objects.select_related('owner','project')[:500]: add('Dataset', d.title, f"Owner {d.owner}. Project {d.project}. Deskripsi {d.description}. Kamus data {d.data_dictionary}. Akses {d.access_level}. Versi {d.version}. URL {d.repository_url}", reverse('dataset_detail', args=[d.pk]))
    for repo in SourceCodeRepository.objects.select_related('project')[:500]: add('Source Code', repo.name, f"Project {repo.project}. URL {repo.url}. Stack {repo.technology_stack}. Lisensi {repo.license}. Visibilitas {repo.visibility}", reverse('repository_detail', args=[repo.pk]))
    for k in KPIRecord.objects.select_related('owner')[:800]: add('KPI', k.name, f"Kategori {k.get_category_display()}. Tahun {k.year}. Target {k.target_value}. Aktual {k.actual_value}. Unit {k.unit}. Capaian {k.achievement_percent} persen. Owner {k.owner}. Catatan {k.notes}", reverse('kpi_detail', args=[k.pk]))
    for asset in LabAsset.objects.all()[:500]: add('Aset', asset.name, f"Kode {asset.asset_code}. Kategori {asset.category}. Lokasi {asset.location}. Status {asset.get_status_display()}. Nilai {asset.value}. Catatan {asset.notes}", reverse('asset_detail', args=[asset.pk]))
    for b in RoomBooking.objects.select_related('requester','approved_by')[:500]: add('Booking Ruang', b.purpose, f"Ruang {b.room_name}. Pemohon {b.requester}. Mulai {b.start_time}. Akhir {b.end_time}. Status {b.get_status_display()}. Approver {b.approved_by}", reverse('booking_detail', args=[b.pk]))
    for s in ProfessionalService.objects.select_related('coordinator','partner')[:800]: add('Layanan Profesional', s.title, f"Tipe {s.get_service_type_display()}. Audiens {s.get_audience_display()}. Skema {s.get_pricing_display()}. Status {s.get_status_display()}. Koordinator {s.coordinator}. Mitra {s.partner}. Pemohon {s.requester_name} dari {s.requester_organization}. Deskripsi {s.description}. Luaran {s.deliverables}. Harga {s.price}. Pendapatan {s.revenue}. Kepuasan {s.satisfaction_score}. Catatan {s.notes}", reverse('professional_service_detail', args=[s.pk]))
    for q in QualityCycleRecord.objects.select_related('owner')[:800]: add('PPEPP', q.title, f"Domain {q.get_domain_display()}. Tahap {q.get_stage_display()}. Periode {q.period}. PIC {q.owner}. Status {q.get_status_display()}. Standar {q.standard}. Pelaksanaan {q.implementation_summary}. Temuan evaluasi {q.evaluation_findings}. Tindakan koreksi {q.corrective_action}. Bukti {q.evidence_url}", reverse('quality_cycle_detail', args=[q.pk]))
    for w in WorkPlanBudget.objects.select_related('owner','funding_source')[:800]: add('RKAT', w.program_name, f"Tahun {w.year}. Area {w.get_area_display()}. Anggaran {w.budget}. Realisasi {w.realization}. Serapan {w.absorption_percent} persen. Sumber dana {w.funding_source}. Status {w.get_status_display()}. Owner {w.owner}. Catatan {w.notes}", reverse('workplan_detail', args=[w.pk]))
    for sop in SOPDocument.objects.select_related('owner')[:800]: add('SOP', sop.title, f"Kode {sop.code}. Area {sop.get_area_display()}. Versi {sop.version}. Status {sop.get_status_display()}. Owner {sop.owner}. Tanggal berlaku {sop.effective_date}. Tanggal review {sop.review_date}. Dokumen {sop.document_url}. Deskripsi {sop.description}", reverse('sop_detail', args=[sop.pk]))
    for pc in PracticumCourse.objects.select_related('coordinator')[:800]: add('Praktikum', pc.course_name, f"Kode {pc.course_code}. Prodi {pc.study_program}. Semester {pc.semester}. Tahun akademik {pc.academic_year}. Koordinator {pc.coordinator}. Status modul {pc.get_module_status_display()}. URL modul {pc.module_url}. Implementasi {pc.implementation_notes}. Evaluasi {pc.evaluation_summary}", reverse('practicum_detail', args=[pc.pk]))
    for cs in CurriculumSupport.objects.select_related('owner')[:500]: add('Dukungan Kurikulum', str(cs), f"Prodi {cs.study_program}. Tahun kurikulum {cs.curriculum_year}. Mata kuliah {cs.course_name}. Kontribusi {cs.get_contribution_type_display()}. Status {cs.get_status_display()}. PIC {cs.owner}. Rekomendasi {cs.recommendation}. Bukti {cs.evidence_url}", reverse('curriculum_support_detail', args=[cs.pk]))
    for rm in RoadmapItem.objects.select_related('owner','owner_group')[:500]: add('Roadmap', rm.title, f"Area {rm.get_area_display()}. Tema {rm.theme}. Periode {rm.start_year}-{rm.end_year}. Prioritas {rm.get_priority_display()}. Status {rm.get_status_display()}. Kelompok {rm.owner_group}. PIC {rm.owner}. Selaras kebijakan {rm.alignment_policy}. Output {rm.expected_outputs}", reverse('roadmap_detail', args=[rm.pk]))
    for tp in TalentProgram.objects.select_related('coordinator')[:500]: add('Talenta', tp.title, f"Tipe {tp.get_program_type_display()}. Status {tp.get_status_display()}. Koordinator {tp.coordinator}. Periode {tp.period}. Kriteria seleksi {tp.selection_criteria}. Rencana pembinaan {tp.mentoring_plan}. Hasil {tp.result_summary}", reverse('talent_program_detail', args=[tp.pk]))
    for dc in DigitalChannel.objects.select_related('owner')[:500]: add('Kanal Digital', dc.name, f"Tipe {dc.get_channel_type_display()}. URL {dc.url}. PIC {dc.owner}. Audiens {dc.audience}. Status {dc.get_status_display()}. Strategi konten {dc.content_strategy}. Catatan performa {dc.performance_notes}", reverse('digital_channel_detail', args=[dc.pk]))
    for ss in SatisfactionSurvey.objects.select_related('owner')[:500]: add('Kepuasan Pengguna', str(ss), f"Domain {ss.get_domain_display()}. Periode {ss.period}. Segmen responden {ss.respondent_segment}. Skor {ss.score}. Sampel {ss.sample_size}. Ringkasan {ss.summary}. Tindak lanjut {ss.follow_up}. Owner {ss.owner}", reverse('satisfaction_survey_detail', args=[ss.pk]))
    for pr in PerformanceReport.objects.select_related('prepared_by','approved_by')[:500]: add('Laporan Kinerja', pr.title, f"Tahun {pr.year}. Tipe {pr.get_report_type_display()}. Status {pr.get_status_display()}. Penyusun {pr.prepared_by}. Approver {pr.approved_by}. Ringkasan {pr.executive_summary}. Dokumen {pr.document_url}. Disampaikan {pr.submitted_at}", reverse('performance_report_detail', args=[pr.pk]))
    for ha in HeadApproval.objects.select_related('requester','approver')[:500]: add('Otorisasi Kepala Lab', ha.title, f"Jenis {ha.get_decision_type_display()}. Status {ha.get_status_display()}. Pemohon {ha.requester}. Approver {ha.approver}. Referensi {ha.subject_reference}. Rationale {ha.rationale}. Catatan keputusan {ha.decision_notes}. Bukti {ha.evidence_url}", reverse('head_approval_detail', args=[ha.pk]))
    return docs

def _rank_docs(question, docs, kind_filter=''):
    q_tokens=_tokenize(question)
    if kind_filter:
        docs=[d for d in docs if d['kind']==kind_filter]
    if not q_tokens:
        return []
    df=Counter()
    for d in docs:
        for t in set(d['tokens']): df[t]+=1
    n=max(len(docs),1)
    phrase=question.lower().strip()
    ranked=[]
    for d in docs:
        tf=Counter(d['tokens'])
        score=0.0
        for t in q_tokens:
            if t in tf:
                idf=math.log((n+1)/(df[t]+1))+1
                score += (1 + math.log(tf[t])) * idf
        title_lower=d['title'].lower()
        text_lower=d['text'].lower()
        for t in q_tokens:
            if t in title_lower: score += 3.5
        if phrase and len(phrase) > 4 and phrase in (title_lower+' '+text_lower): score += 8
        if score>0:
            d=dict(d); d['score']=round(score,2); ranked.append(d)
    return sorted(ranked, key=lambda x:x['score'], reverse=True)

def _build_answer(question, sources):
    if not sources:
        return ('Saya belum menemukan informasi yang relevan di database internal untuk pertanyaan tersebut. '
                'Coba gunakan kata kunci yang lebih spesifik, misalnya nama dosen, topik riset, tahun publikasi, nama mitra, atau jenis KPI.')
    by_kind=defaultdict(list)
    for s in sources:
        by_kind[s['kind']].append(s)
    lines=[]
    lines.append('Jawaban berbasis retrieval data internal webapp:')
    lines.append('')
    lines.append(f'Saya menemukan {len(sources)} sumber paling relevan untuk pertanyaan: “{question}”.')
    lines.append('')
    for kind, items in by_kind.items():
        lines.append(f'{kind}:')
        for item in items[:4]:
            snippet=item['text'][:420].strip()
            lines.append(f'- {item["title"]}: {snippet}')
        lines.append('')
    lines.append('Catatan validasi: jawaban ini disusun dari data tersimpan di modul webapp. Untuk keputusan formal, buka sumber terkait dan validasi metadata terbaru.')
    return '\n'.join(lines)

@login_required
def rag_chatbot(request):
    answer=''; sources=[]; question=''; kind=request.POST.get('kind','') if request.method=='POST' else request.GET.get('kind','')
    docs=_rag_corpus()
    kind_choices=[('', 'Semua Modul'),('Anggota','Anggota'),('Kelompok Riset','Kelompok Riset'),('Penelitian','Penelitian'),('Pengabdian','Pengabdian'),('Layanan Profesional','Layanan Profesional'),('Publikasi','Publikasi'),('Mitra','Mitra'),('Perjanjian','Perjanjian'),('Dataset','Dataset'),('Source Code','Source Code'),('KPI','KPI'),('Aset','Aset'),('Booking Ruang','Booking Ruang'),('PPEPP','PPEPP'),('RKAT','RKAT'),('SOP','SOP'),('Praktikum','Praktikum'),('Dukungan Kurikulum','Dukungan Kurikulum'),('Roadmap','Roadmap'),('Talenta','Talenta'),('Kanal Digital','Kanal Digital'),('Kepuasan Pengguna','Kepuasan Pengguna'),('Laporan Kinerja','Laporan Kinerja'),('Otorisasi Kepala Lab','Otorisasi Kepala Lab')]
    if request.method=='POST':
        question=request.POST.get('question','').strip()
        if question:
            sources=_rank_docs(question, docs, kind_filter=kind)[:10]
            answer=_build_answer(question, sources)
    stats={'docs':len(docs),'research':ResearchProject.objects.count(),'members':MemberProfile.objects.count(),'publications':Publication.objects.count()}
    return render(request,'enterprise/rag_chatbot.html',{'answer':answer,'sources':sources,'question':question,'stats':stats,'kind':kind,'kind_choices':kind_choices})

@login_required
def api_summary(request):
    return JsonResponse({
        'research_projects': ResearchProject.objects.count(),
        'community_service_projects': CommunityServiceProject.objects.count(),
        'publications': Publication.objects.count(),
        'partners': Partner.objects.count(),
        'agreements_active': CollaborationAgreement.objects.filter(status='ACTIVE').count(),
        'assets': LabAsset.objects.count(),
        'kpi_records': KPIRecord.objects.count(),
        'professional_services': ProfessionalService.objects.count(),
        'ppepp_records': QualityCycleRecord.objects.count(),
        'workplans': WorkPlanBudget.objects.count(),
        'sop_documents': SOPDocument.objects.count(),
        'practicum_courses': PracticumCourse.objects.count(),
        'curriculum_supports': CurriculumSupport.objects.count(),
        'roadmap_items': RoadmapItem.objects.count(),
        'talent_programs': TalentProgram.objects.count(),
        'digital_channels': DigitalChannel.objects.count(),
        'satisfaction_surveys': SatisfactionSurvey.objects.count(),
        'performance_reports': PerformanceReport.objects.count(),
        'head_approvals': HeadApproval.objects.count(),
    })
