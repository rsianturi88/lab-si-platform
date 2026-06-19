from django.conf import settings
from django.db import models
from memberships.models import TimeStampedModel, MemberProfile, ResearchGroup

class OrganizationUnit(TimeStampedModel):
    name = models.CharField(max_length=180, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class LabPosition(TimeStampedModel):
    title = models.CharField(max_length=150)
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='positions')
    unit = models.ForeignKey(OrganizationUnit, null=True, blank=True, on_delete=models.SET_NULL)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    responsibility = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['-start_date', 'title']
        indexes = [models.Index(fields=['title', 'is_active'])]
    def __str__(self): return f'{self.title} - {self.member}'

class FundingSource(TimeStampedModel):
    name = models.CharField(max_length=180, unique=True)
    category = models.CharField(max_length=80, blank=True, help_text='Internal, DIPA, BRIN, Industri, Internasional')
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class ResearchProject(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT='DRAFT','Draft'
        PROPOSAL='PROPOSAL','Proposal'
        REVIEW='REVIEW','Review'
        FUNDED='FUNDED','Didanai'
        ONGOING='ONGOING','Berjalan'
        COMPLETED='COMPLETED','Selesai'
        CANCELLED='CANCELLED','Dibatalkan'
    class Scheme(models.TextChoices):
        INTERNAL='INTERNAL','Internal Universitas'
        DIPA='DIPA','DIPA/Unggulan'
        NATIONAL='NATIONAL','Nasional'
        INDUSTRY='INDUSTRY','Industri'
        INTERNATIONAL='INTERNATIONAL','Internasional'
        INDEPENDENT='INDEPENDENT','Mandiri'
    title = models.CharField(max_length=260)
    abstract = models.TextField(blank=True)
    scheme = models.CharField(max_length=30, choices=Scheme.choices, default=Scheme.INTERNAL)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    research_group = models.ForeignKey(ResearchGroup, null=True, blank=True, on_delete=models.SET_NULL)
    leader = models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='led_research_projects')
    members = models.ManyToManyField(MemberProfile, blank=True, related_name='research_projects')
    funding_source = models.ForeignKey(FundingSource, null=True, blank=True, on_delete=models.SET_NULL)
    budget = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    keywords = models.CharField(max_length=300, blank=True)
    expected_outputs = models.TextField(blank=True)
    risks = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status','scheme']), models.Index(fields=['start_date'])]
    def __str__(self): return self.title

class CommunityServiceProject(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT='DRAFT','Draft'
        PROPOSAL='PROPOSAL','Proposal'
        ONGOING='ONGOING','Berjalan'
        COMPLETED='COMPLETED','Selesai'
        CANCELLED='CANCELLED','Dibatalkan'
    title = models.CharField(max_length=260)
    partner_name = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    leader = models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='led_service_projects')
    members = models.ManyToManyField(MemberProfile, blank=True, related_name='service_projects')
    funding_source = models.ForeignKey(FundingSource, null=True, blank=True, on_delete=models.SET_NULL)
    budget = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    output_summary = models.TextField(blank=True)
    outcome_summary = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta: ordering = ['-created_at']
    def __str__(self): return self.title

class Publication(TimeStampedModel):
    class PubType(models.TextChoices):
        JOURNAL='JOURNAL','Jurnal'
        CONFERENCE='CONFERENCE','Konferensi'
        BOOK='BOOK','Buku/Bab Buku'
        IPR='IPR','HKI/Paten'
        OTHER='OTHER','Lainnya'
    class Indexing(models.TextChoices):
        SCOPUS_Q1='SCOPUS_Q1','Scopus Q1'
        SCOPUS_Q2='SCOPUS_Q2','Scopus Q2'
        SCOPUS_Q3='SCOPUS_Q3','Scopus Q3'
        SCOPUS_Q4='SCOPUS_Q4','Scopus Q4'
        SINTA_1='SINTA_1','SINTA 1'
        SINTA_2='SINTA_2','SINTA 2'
        SINTA_3='SINTA_3','SINTA 3'
        NON_INDEXED='NON_INDEXED','Non-indexed'
    title = models.CharField(max_length=300)
    publication_type = models.CharField(max_length=30, choices=PubType.choices, default=PubType.JOURNAL)
    indexing = models.CharField(max_length=30, choices=Indexing.choices, default=Indexing.NON_INDEXED)
    authors = models.ManyToManyField(MemberProfile, blank=True, related_name='publications')
    project = models.ForeignKey(ResearchProject, null=True, blank=True, on_delete=models.SET_NULL, related_name='publications')
    venue = models.CharField(max_length=220, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    doi = models.CharField(max_length=180, blank=True)
    url = models.URLField(blank=True)
    citation_count = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['-year', 'title']
        indexes = [models.Index(fields=['year','indexing'])]
    def __str__(self): return self.title

class Dataset(TimeStampedModel):
    title = models.CharField(max_length=240)
    owner = models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='datasets')
    project = models.ForeignKey(ResearchProject, null=True, blank=True, on_delete=models.SET_NULL, related_name='datasets')
    description = models.TextField(blank=True)
    data_dictionary = models.TextField(blank=True)
    access_level = models.CharField(max_length=60, default='Internal')
    version = models.CharField(max_length=30, default='1.0.0')
    repository_url = models.URLField(blank=True)
    def __str__(self): return self.title

class SourceCodeRepository(TimeStampedModel):
    name = models.CharField(max_length=180)
    project = models.ForeignKey(ResearchProject, null=True, blank=True, on_delete=models.SET_NULL, related_name='repositories')
    url = models.URLField()
    technology_stack = models.CharField(max_length=250, blank=True)
    license = models.CharField(max_length=80, blank=True)
    visibility = models.CharField(max_length=40, default='Private')
    def __str__(self): return self.name

class Partner(TimeStampedModel):
    class PartnerType(models.TextChoices):
        INDUSTRY='INDUSTRY','Industri'
        GOVERNMENT='GOVERNMENT','Pemerintah'
        UNIVERSITY='UNIVERSITY','Perguruan Tinggi'
        SCHOOL='SCHOOL','Sekolah'
        COMMUNITY='COMMUNITY','Komunitas'
        ALUMNI='ALUMNI','Alumni'
    name = models.CharField(max_length=200, unique=True)
    partner_type = models.CharField(max_length=30, choices=PartnerType.choices)
    contact_person = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True)
    strategic_value = models.TextField(blank=True)
    def __str__(self): return self.name

class CollaborationAgreement(TimeStampedModel):
    class AgreementType(models.TextChoices):
        MOU='MOU','MoU'
        MOA='MOA','MoA'
        IA='IA','Implementation Arrangement'
        NDA='NDA','NDA'
        CONTRACT='CONTRACT','Kontrak'
    class Status(models.TextChoices):
        DRAFT='DRAFT','Draft'
        REVIEW='REVIEW','Review'
        ACTIVE='ACTIVE','Aktif'
        EXPIRED='EXPIRED','Kedaluwarsa'
        TERMINATED='TERMINATED','Dihentikan'
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='agreements')
    title = models.CharField(max_length=240)
    agreement_type = models.CharField(max_length=30, choices=AgreementType.choices)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    document_url = models.URLField(blank=True)
    scope = models.TextField(blank=True)
    owner = models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta: ordering = ['-start_date']
    def __str__(self): return self.title

class LabAsset(TimeStampedModel):
    class Status(models.TextChoices):
        AVAILABLE='AVAILABLE','Tersedia'
        BORROWED='BORROWED','Dipinjam'
        MAINTENANCE='MAINTENANCE','Perawatan'
        RETIRED='RETIRED','Tidak Aktif'
    asset_code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=180)
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.AVAILABLE)
    acquisition_date = models.DateField(null=True, blank=True)
    value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    def __str__(self): return f'{self.asset_code} - {self.name}'

class RoomBooking(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED='REQUESTED','Diajukan'
        APPROVED='APPROVED','Disetujui'
        REJECTED='REJECTED','Ditolak'
        CANCELLED='CANCELLED','Dibatalkan'
    room_name = models.CharField(max_length=150)
    requester = models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    purpose = models.CharField(max_length=240)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.REQUESTED)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta: ordering = ['-start_time']
    def __str__(self): return f'{self.room_name} - {self.purpose}'

class KPIRecord(TimeStampedModel):
    class Category(models.TextChoices):
        RESEARCH='RESEARCH','Penelitian'
        PUBLICATION='PUBLICATION','Publikasi'
        SERVICE='SERVICE','Pengabdian'
        PARTNERSHIP='PARTNERSHIP','Kerja Sama'
        TALENT='TALENT','Talenta'
        FINANCE='FINANCE','Keuangan'
    category = models.CharField(max_length=30, choices=Category.choices)
    name = models.CharField(max_length=180)
    year = models.PositiveIntegerField()
    target_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, blank=True)
    owner = models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    class Meta:
        unique_together = ('category','name','year')
        ordering = ['-year','category','name']
    @property
    def achievement_percent(self):
        return 0 if not self.target_value else round(float(self.actual_value / self.target_value * 100), 2)
    def __str__(self): return f'{self.name} {self.year}'


class ProfessionalService(TimeStampedModel):
    class ServiceType(models.TextChoices):
        TRAINING='TRAINING','Pelatihan'
        CONSULTING='CONSULTING','Konsultasi'
        SYSTEM_DEVELOPMENT='SYSTEM_DEVELOPMENT','Pengembangan Sistem'
        DATA_ANALYTICS='DATA_ANALYTICS','Analitik Data'
        AUDIT='AUDIT','Audit/Tata Kelola SI'
        WORKSHOP='WORKSHOP','Workshop'
        OTHER='OTHER','Lainnya'
    class Audience(models.TextChoices):
        INTERNAL='INTERNAL','Internal FILKOM/UB'
        EXTERNAL='EXTERNAL','Eksternal'
        BOTH='BOTH','Internal dan Eksternal'
    class Pricing(models.TextChoices):
        FREE='FREE','Gratis'
        PAID='PAID','Berbayar'
        HYBRID='HYBRID','Gratis dan Berbayar'
    class Status(models.TextChoices):
        DRAFT='DRAFT','Draft'
        AVAILABLE='AVAILABLE','Tersedia'
        REQUESTED='REQUESTED','Diajukan'
        ONGOING='ONGOING','Berjalan'
        COMPLETED='COMPLETED','Selesai'
        CANCELLED='CANCELLED','Dibatalkan'
    title=models.CharField(max_length=240)
    service_type=models.CharField(max_length=40, choices=ServiceType.choices, default=ServiceType.CONSULTING)
    audience=models.CharField(max_length=30, choices=Audience.choices, default=Audience.BOTH)
    pricing=models.CharField(max_length=30, choices=Pricing.choices, default=Pricing.FREE)
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    coordinator=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='coordinated_professional_services')
    experts=models.ManyToManyField(MemberProfile, blank=True, related_name='professional_services')
    partner=models.ForeignKey(Partner, null=True, blank=True, on_delete=models.SET_NULL, related_name='professional_services')
    requester_name=models.CharField(max_length=180, blank=True)
    requester_organization=models.CharField(max_length=220, blank=True)
    requester_contact=models.CharField(max_length=120, blank=True)
    requester_email=models.EmailField(blank=True)
    description=models.TextField(blank=True)
    deliverables=models.TextField(blank=True)
    price=models.DecimalField(max_digits=16, decimal_places=2, default=0)
    revenue=models.DecimalField(max_digits=16, decimal_places=2, default=0)
    start_date=models.DateField(null=True, blank=True)
    end_date=models.DateField(null=True, blank=True)
    satisfaction_score=models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text='Skor 1-5')
    notes=models.TextField(blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        ordering=['-created_at']
        indexes=[models.Index(fields=['service_type','pricing','status']), models.Index(fields=['audience','status'])]
    def __str__(self): return self.title

class QualityCycleRecord(TimeStampedModel):
    class Domain(models.TextChoices):
        PRACTICUM='PRACTICUM','Praktikum'
        RESEARCH='RESEARCH','Riset dan Inovasi'
        COMMUNITY_SERVICE='COMMUNITY_SERVICE','Pengabdian kepada Masyarakat'
        PROFESSIONAL_SERVICE='PROFESSIONAL_SERVICE','Layanan Profesional'
        FACILITY='FACILITY','Fasilitas Laboratorium'
    class Stage(models.TextChoices):
        PENETAPAN='PENETAPAN','Penetapan'
        PELAKSANAAN='PELAKSANAAN','Pelaksanaan'
        EVALUASI='EVALUASI','Evaluasi'
        PENGENDALIAN='PENGENDALIAN','Pengendalian'
        PENINGKATAN='PENINGKATAN','Peningkatan'
    class Status(models.TextChoices):
        PLANNED='PLANNED','Direncanakan'
        ONGOING='ONGOING','Berjalan'
        DONE='DONE','Selesai'
        NEEDS_ACTION='NEEDS_ACTION','Perlu Tindak Lanjut'
    title=models.CharField(max_length=240)
    domain=models.CharField(max_length=40, choices=Domain.choices)
    stage=models.CharField(max_length=30, choices=Stage.choices)
    period=models.CharField(max_length=80, help_text='Contoh: 2026 Genap / 2026 Tahunan')
    owner=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.PLANNED)
    standard=models.TextField(blank=True)
    implementation_summary=models.TextField(blank=True)
    evaluation_findings=models.TextField(blank=True)
    corrective_action=models.TextField(blank=True)
    due_date=models.DateField(null=True, blank=True)
    evidence_url=models.URLField(blank=True)
    class Meta:
        ordering=['-created_at']
        indexes=[models.Index(fields=['domain','stage','status'])]
    def __str__(self): return f'{self.title} - {self.get_stage_display()}'

class WorkPlanBudget(TimeStampedModel):
    class Area(models.TextChoices):
        PRACTICUM='PRACTICUM','Praktikum'
        RESEARCH='RESEARCH','Riset dan Inovasi'
        COMMUNITY_SERVICE='COMMUNITY_SERVICE','Pengabdian'
        PROFESSIONAL_SERVICE='PROFESSIONAL_SERVICE','Layanan Profesional'
        FACILITY='FACILITY','Fasilitas/Aset'
        COMMUNICATION='COMMUNICATION','Komunikasi Digital'
    class Status(models.TextChoices):
        DRAFT='DRAFT','Draft'
        REVIEW='REVIEW','Review'
        APPROVED='APPROVED','Disetujui'
        REVISION='REVISION','Revisi'
        COMPLETED='COMPLETED','Selesai'
    year=models.PositiveIntegerField()
    program_name=models.CharField(max_length=240)
    area=models.CharField(max_length=40, choices=Area.choices)
    budget=models.DecimalField(max_digits=16, decimal_places=2, default=0)
    realization=models.DecimalField(max_digits=16, decimal_places=2, default=0)
    funding_source=models.ForeignKey(FundingSource, null=True, blank=True, on_delete=models.SET_NULL)
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    owner=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    approved_by=models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    notes=models.TextField(blank=True)
    class Meta:
        ordering=['-year','program_name']
        indexes=[models.Index(fields=['year','area','status'])]
    @property
    def absorption_percent(self):
        return 0 if not self.budget else round(float(self.realization / self.budget * 100),2)
    def __str__(self): return f'{self.program_name} ({self.year})'

class SOPDocument(TimeStampedModel):
    class Area(models.TextChoices):
        PRACTICUM='PRACTICUM','Praktikum'
        RESEARCH='RESEARCH','Riset dan Inovasi'
        COMMUNITY_SERVICE='COMMUNITY_SERVICE','Pengabdian'
        PROFESSIONAL_SERVICE='PROFESSIONAL_SERVICE','Layanan Profesional'
        FACILITY='FACILITY','Fasilitas/Aset'
        GOVERNANCE='GOVERNANCE','Tata Kelola'
    class Status(models.TextChoices):
        DRAFT='DRAFT','Draft'
        REVIEW='REVIEW','Review'
        APPROVED='APPROVED','Disetujui'
        OBSOLETE='OBSOLETE','Tidak Berlaku'
    code=models.CharField(max_length=80, unique=True)
    title=models.CharField(max_length=240)
    area=models.CharField(max_length=40, choices=Area.choices)
    version=models.CharField(max_length=40, default='1.0')
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    owner=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    effective_date=models.DateField(null=True, blank=True)
    review_date=models.DateField(null=True, blank=True)
    document_url=models.URLField(blank=True)
    description=models.TextField(blank=True)
    class Meta: ordering=['area','code']
    def __str__(self): return f'{self.code} - {self.title}'

class PracticumCourse(TimeStampedModel):
    class ModuleStatus(models.TextChoices):
        DRAFT='DRAFT','Draft'
        READY='READY','Siap Digunakan'
        NEEDS_REVISION='NEEDS_REVISION','Perlu Revisi'
        ARCHIVED='ARCHIVED','Arsip'
    course_code=models.CharField(max_length=40)
    course_name=models.CharField(max_length=220)
    study_program=models.CharField(max_length=160)
    semester=models.CharField(max_length=40, blank=True)
    academic_year=models.CharField(max_length=40)
    coordinator=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='coordinated_practicums')
    assistants=models.ManyToManyField(MemberProfile, blank=True, related_name='assisted_practicums')
    module_status=models.CharField(max_length=30, choices=ModuleStatus.choices, default=ModuleStatus.DRAFT)
    module_url=models.URLField(blank=True)
    implementation_notes=models.TextField(blank=True)
    evaluation_summary=models.TextField(blank=True)
    class Meta:
        ordering=['-academic_year','course_code']
        unique_together=('course_code','academic_year','study_program')
    def __str__(self): return f'{self.course_code} - {self.course_name}'

class CurriculumSupport(TimeStampedModel):
    class ContributionType(models.TextChoices):
        CPL='CPL','CPL/ILO'
        CPMK='CPMK','CPMK/CLO'
        MODULE='MODULE','Modul Praktikum'
        ASSESSMENT='ASSESSMENT','Asesmen'
        ROADMAP='ROADMAP','Peta Keilmuan'
    class Status(models.TextChoices):
        DRAFT='DRAFT','Draft'
        REVIEW='REVIEW','Review Prodi'
        SUBMITTED='SUBMITTED','Disampaikan ke Prodi'
        ACCEPTED='ACCEPTED','Diterima'
        REVISION='REVISION','Perlu Revisi'
    study_program=models.CharField(max_length=160)
    curriculum_year=models.PositiveIntegerField()
    course_name=models.CharField(max_length=220, blank=True)
    contribution_type=models.CharField(max_length=30, choices=ContributionType.choices)
    owner=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    recommendation=models.TextField()
    evidence_url=models.URLField(blank=True)
    class Meta: ordering=['-curriculum_year','study_program']
    def __str__(self): return f'{self.study_program} {self.curriculum_year} - {self.get_contribution_type_display()}'

class RoadmapItem(TimeStampedModel):
    class Area(models.TextChoices):
        RESEARCH='RESEARCH','Riset'
        INNOVATION='INNOVATION','Inovasi'
        COMMUNITY_SERVICE='COMMUNITY_SERVICE','Pengabdian Berbasis Riset'
        PROFESSIONAL_SERVICE='PROFESSIONAL_SERVICE','Layanan Profesional'
    class Priority(models.TextChoices):
        LOW='LOW','Rendah'
        MEDIUM='MEDIUM','Sedang'
        HIGH='HIGH','Tinggi'
        STRATEGIC='STRATEGIC','Strategis'
    class Status(models.TextChoices):
        PLANNED='PLANNED','Direncanakan'
        ONGOING='ONGOING','Berjalan'
        ACHIEVED='ACHIEVED','Tercapai'
        REVISED='REVISED','Direvisi'
    title=models.CharField(max_length=240)
    area=models.CharField(max_length=40, choices=Area.choices)
    theme=models.CharField(max_length=180)
    start_year=models.PositiveIntegerField()
    end_year=models.PositiveIntegerField()
    priority=models.CharField(max_length=30, choices=Priority.choices, default=Priority.MEDIUM)
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.PLANNED)
    owner_group=models.ForeignKey(ResearchGroup, null=True, blank=True, on_delete=models.SET_NULL)
    owner=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    alignment_policy=models.TextField(blank=True)
    expected_outputs=models.TextField(blank=True)
    class Meta: ordering=['start_year','priority','title']
    def __str__(self): return self.title

class TalentProgram(TimeStampedModel):
    class ProgramType(models.TextChoices):
        PRACTICUM_ASSISTANT='PRACTICUM_ASSISTANT','Asisten Praktikum'
        RESEARCH_ASSISTANT='RESEARCH_ASSISTANT','Asisten Riset'
        COMPETITION='COMPETITION','Kompetisi Ilmiah'
        COACHING='COACHING','Pembinaan Kompetensi'
    class Status(models.TextChoices):
        PLANNED='PLANNED','Direncanakan'
        OPEN='OPEN','Pendaftaran Dibuka'
        SELECTION='SELECTION','Seleksi'
        ONGOING='ONGOING','Pembinaan Berjalan'
        COMPLETED='COMPLETED','Selesai'
    title=models.CharField(max_length=240)
    program_type=models.CharField(max_length=40, choices=ProgramType.choices)
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.PLANNED)
    coordinator=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='coordinated_talent_programs')
    participants=models.ManyToManyField(MemberProfile, blank=True, related_name='talent_programs')
    period=models.CharField(max_length=80)
    selection_criteria=models.TextField(blank=True)
    mentoring_plan=models.TextField(blank=True)
    result_summary=models.TextField(blank=True)
    class Meta: ordering=['-created_at','title']
    def __str__(self): return self.title

class DigitalChannel(TimeStampedModel):
    class ChannelType(models.TextChoices):
        WEBSITE='WEBSITE','Website'
        INSTAGRAM='INSTAGRAM','Instagram'
        YOUTUBE='YOUTUBE','YouTube'
        LINKEDIN='LINKEDIN','LinkedIn'
        EMAIL='EMAIL','Email/Newsletter'
        OTHER='OTHER','Lainnya'
    class Status(models.TextChoices):
        ACTIVE='ACTIVE','Aktif'
        INACTIVE='INACTIVE','Tidak Aktif'
        PLANNED='PLANNED','Direncanakan'
    name=models.CharField(max_length=180)
    channel_type=models.CharField(max_length=30, choices=ChannelType.choices)
    url=models.URLField(blank=True)
    owner=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    audience=models.CharField(max_length=180, blank=True)
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.ACTIVE)
    content_strategy=models.TextField(blank=True)
    last_update=models.DateField(null=True, blank=True)
    performance_notes=models.TextField(blank=True)
    class Meta: ordering=['channel_type','name']
    def __str__(self): return self.name

class SatisfactionSurvey(TimeStampedModel):
    class Domain(models.TextChoices):
        PRACTICUM='PRACTICUM','Praktikum'
        RESEARCH='RESEARCH','Riset dan Inovasi'
        COMMUNITY_SERVICE='COMMUNITY_SERVICE','Pengabdian'
        PROFESSIONAL_SERVICE='PROFESSIONAL_SERVICE','Layanan Profesional'
        FACILITY='FACILITY','Fasilitas'
    domain=models.CharField(max_length=40, choices=Domain.choices)
    period=models.CharField(max_length=80)
    respondent_segment=models.CharField(max_length=160)
    score=models.DecimalField(max_digits=4, decimal_places=2, help_text='Skor 1-5')
    sample_size=models.PositiveIntegerField(default=0)
    summary=models.TextField(blank=True)
    follow_up=models.TextField(blank=True)
    owner=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta: ordering=['-created_at']
    def __str__(self): return f'{self.get_domain_display()} {self.period} - {self.score}'

class PerformanceReport(TimeStampedModel):
    class ReportType(models.TextChoices):
        ANNUAL='ANNUAL','Tahunan'
        SEMESTER='SEMESTER','Semester'
        SPECIAL='SPECIAL','Khusus'
    class Status(models.TextChoices):
        DRAFT='DRAFT','Draft'
        REVIEW='REVIEW','Review'
        APPROVED='APPROVED','Disahkan'
        SUBMITTED='SUBMITTED','Disampaikan ke Dekan'
    year=models.PositiveIntegerField()
    report_type=models.CharField(max_length=30, choices=ReportType.choices, default=ReportType.ANNUAL)
    title=models.CharField(max_length=240)
    prepared_by=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='prepared_reports')
    approved_by=models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    executive_summary=models.TextField(blank=True)
    document_url=models.URLField(blank=True)
    submitted_at=models.DateField(null=True, blank=True)
    class Meta: ordering=['-year','title']
    def __str__(self): return self.title

class HeadApproval(TimeStampedModel):
    class DecisionType(models.TextChoices):
        SOP='SOP','Pengesahan SOP'
        BUDGET='BUDGET','Persetujuan RKAT/Anggaran'
        ASSISTANT_ASSIGNMENT='ASSISTANT_ASSIGNMENT','Penugasan Asisten'
        ROADMAP='ROADMAP','Persetujuan Roadmap'
        ASSET='ASSET','Kebutuhan/Pemeliharaan Aset'
        SERVICE='SERVICE','Layanan Profesional'
        REPORT='REPORT','Laporan Kinerja'
        OTHER='OTHER','Lainnya'
    class Status(models.TextChoices):
        REQUESTED='REQUESTED','Diajukan'
        APPROVED='APPROVED','Disetujui'
        REJECTED='REJECTED','Ditolak'
        REVISION='REVISION','Perlu Revisi'
    title=models.CharField(max_length=240)
    decision_type=models.CharField(max_length=40, choices=DecisionType.choices)
    requester=models.ForeignKey(MemberProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='approval_requests')
    approver=models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='lab_approvals')
    status=models.CharField(max_length=30, choices=Status.choices, default=Status.REQUESTED)
    requested_at=models.DateField(null=True, blank=True)
    decided_at=models.DateField(null=True, blank=True)
    subject_reference=models.CharField(max_length=240, blank=True, help_text='Referensi objek: SOP/RKAT/Roadmap/Layanan/lainnya')
    rationale=models.TextField(blank=True)
    decision_notes=models.TextField(blank=True)
    evidence_url=models.URLField(blank=True)
    class Meta: ordering=['-created_at']
    def __str__(self): return self.title
