from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from memberships.models import ResearchGroup, MemberProfile
from enterprise.models import *

class Command(BaseCommand):
    help='Seed Enterprise Research and Innovation Management Platform demo data'
    def handle(self,*args,**opts):
        User=get_user_model()
        admin=User.objects.filter(is_superuser=True).first()
        groups=[]
        for name in ['Business Process Management','Artificial Intelligence','Data Analytics','Digital Government','Health Informatics','GIS and Smart City','Smart Agriculture','Enterprise Systems']:
            g,_=ResearchGroup.objects.get_or_create(name=name, defaults={'description':f'Kelompok keahlian {name}'})
            groups.append(g)
        if admin:
            admin_member,_=MemberProfile.objects.get_or_create(user=admin, defaults={'member_type':'LECTURER','status':'ACTIVE','research_group':groups[0],'expertise':'Information Systems, Business Process Management, Research Management','program_study':'Sistem Informasi','position':'Kepala Laboratorium','created_by':admin,'updated_by':admin})
        else:
            admin_member=None
        demo_specs=[
            ('dosen.ai','Dosen','AI','LECTURER','Artificial Intelligence, Machine Learning, RAG','Artificial Intelligence'),
            ('mhs.data','Mahasiswa','Data','STUDENT','Data Analytics, Dashboard, Visualization','Data Analytics'),
            ('mhs.gov','Mahasiswa','Gov','STUDENT','Digital Government, BPMN, Public Sector IS','Digital Government'),
        ]
        for username, first, last, role, expertise, group_name in demo_specs:
            user,_=User.objects.get_or_create(username=username, defaults={'first_name':first,'last_name':last,'email':f'{username}@example.com','role':role,'institution_id':username.upper(),'is_verified':True,'is_active':True})
            if not user.has_usable_password():
                user.set_password('ChangeMe123!'); user.save(update_fields=['password'])
            g=ResearchGroup.objects.filter(name=group_name).first() or groups[0]
            MemberProfile.objects.get_or_create(user=user, defaults={'member_type':'LECTURER' if role=='LECTURER' else 'STUDENT','status':'ACTIVE','research_group':g,'expertise':expertise,'program_study':'Sistem Informasi','position':'Peneliti' if role=='LECTURER' else 'Asisten Peneliti','created_by':admin,'updated_by':admin})
        unit,_=OrganizationUnit.objects.get_or_create(name='Laboratorium Sistem Informasi', defaults={'description':'Unit riset, inovasi, dan layanan akademik sistem informasi.'})
        OrganizationUnit.objects.get_or_create(name='Research and Innovation Office', defaults={'parent':unit})
        OrganizationUnit.objects.get_or_create(name='Industry Collaboration Office', defaults={'parent':unit})
        fs1,_=FundingSource.objects.get_or_create(name='DIPA FILKOM UB', defaults={'category':'Internal'})
        fs2,_=FundingSource.objects.get_or_create(name='Kemitraan Industri', defaults={'category':'Industri'})
        members=list(MemberProfile.objects.select_related('user')[:10])
        leader=admin_member or (members[0] if members else None)
        if leader:
            LabPosition.objects.get_or_create(title='Kepala Laboratorium', member=leader, unit=unit, start_date=date.today().replace(month=1,day=1), defaults={'responsibility':'Mengelola roadmap riset dan inovasi lab.'})
        rp,_=ResearchProject.objects.get_or_create(title='Enterprise Research and Innovation Management Platform untuk Laboratorium Sistem Informasi', defaults={'abstract':'Platform terpadu untuk mengelola portofolio riset, publikasi, mitra, aset, KPI, chatbot RAG, dan knowledge graph berbasis pencarian.', 'scheme':'DIPA','status':'ONGOING','research_group':groups[0], 'leader':leader, 'funding_source':fs1, 'budget':15000000, 'start_date':date.today().replace(month=1,day=1), 'end_date':date.today().replace(month=12,day=31), 'keywords':'research management, innovation platform, laboratory information system, RAG, knowledge graph', 'created_by':admin})
        if members: rp.members.set(members[:3])
        sp,_=CommunityServiceProject.objects.get_or_create(title='Pelatihan AI dan Bank Soal Digital untuk Guru Sekolah Dasar', defaults={'partner_name':'Sekolah Mitra', 'status':'ONGOING', 'leader':leader, 'funding_source':fs1, 'budget':15000000, 'start_date':date.today(), 'output_summary':'Modul pelatihan, bank soal digital, publikasi media massa.', 'outcome_summary':'Peningkatan kompetensi guru dalam penyusunan soal digital.', 'created_by':admin})
        if members: sp.members.set(members[:2])
        pub,_=Publication.objects.get_or_create(title='Applying Zone of Tolerance to a Customer Service App in a Public Higher Education Institution', defaults={'publication_type':'JOURNAL','indexing':'SINTA_2','project':rp,'venue':'The Winners','year':date.today().year,'citation_count':0})
        if members: pub.authors.set(members[:2])
        Partner.objects.get_or_create(name='PT Mitra Teknologi Indonesia', defaults={'partner_type':'INDUSTRY','contact_person':'PIC Industri','email':'pic@example.com','strategic_value':'Mitra potensial untuk magang, riset terapan, dan hilirisasi produk lab.'})
        partner=Partner.objects.first()
        if partner:
            CollaborationAgreement.objects.get_or_create(partner=partner, title='Kerja Sama Riset Terapan dan Pengembangan Produk Digital', defaults={'agreement_type':'MOU','status':'ACTIVE','start_date':date.today(),'end_date':date.today()+timedelta(days=365),'scope':'Riset bersama, magang mahasiswa, kuliah tamu, dan pengembangan produk digital.', 'owner':leader})
        Dataset.objects.get_or_create(title='Dataset Portofolio Riset Lab SI', defaults={'owner':leader,'project':rp,'description':'Dataset internal mengenai penelitian, publikasi, anggota, dan mitra lab.','access_level':'Internal','version':'1.0.0'})
        SourceCodeRepository.objects.get_or_create(name='lab-si-erimp', defaults={'project':rp,'url':'https://github.com/example/lab-si-erimp','technology_stack':'Django, PostgreSQL, Vercel, Neon, Cytoscape.js','license':'Internal','visibility':'Private'})
        LabAsset.objects.get_or_create(asset_code='LABSI-LAP-001', defaults={'name':'Laptop Riset AI','category':'Komputasi','location':'Lab SI','status':'AVAILABLE','value':15000000})
        if leader:
            RoomBooking.objects.get_or_create(room_name='Ruang Diskusi Lab SI', purpose='Rapat roadmap riset', start_time=timezone.now()+timedelta(days=1), defaults={'end_time':timezone.now()+timedelta(days=1,hours=2),'requester':leader,'status':'APPROVED','approved_by':admin})
        year=date.today().year
        for cat,name,target,actual,unit in [('RESEARCH','Jumlah penelitian aktif',5,1,'judul'),('PUBLICATION','Publikasi bereputasi',6,1,'artikel'),('SERVICE','Kegiatan pengabdian',3,1,'kegiatan'),('PARTNERSHIP','Mitra aktif',5,1,'mitra'),('TALENT','Mahasiswa aktif di lab',30,MemberProfile.objects.filter(member_type='STUDENT').count(),'orang')]:
            KPIRecord.objects.get_or_create(category=cat,name=name,year=year,defaults={'target_value':target,'actual_value':actual,'unit':unit,'owner':leader})

        # Governance, service, practicum, and head-of-lab support modules
        ProfessionalService.objects.get_or_create(title='Konsultasi Business Process Management untuk Unit Internal', defaults={'service_type':'CONSULTING','audience':'INTERNAL','pricing':'FREE','status':'AVAILABLE','coordinator':leader,'requester_organization':'FILKOM UB','description':'Layanan konsultasi pemodelan proses bisnis, SOP, dan perbaikan tata kelola unit internal.','deliverables':'Notulensi konsultasi, rekomendasi BPMN, dan rencana tindak lanjut.','price':0,'revenue':0,'created_by':admin})
        ProfessionalService.objects.get_or_create(title='Pelatihan Dashboard dan Analitik Data untuk Mitra Industri', defaults={'service_type':'TRAINING','audience':'EXTERNAL','pricing':'PAID','status':'AVAILABLE','coordinator':leader,'partner':partner,'requester_organization':'PT Mitra Teknologi Indonesia','description':'Pelatihan analitik data, visualisasi, dan dashboard operasional untuk mitra eksternal.','deliverables':'Modul pelatihan, sertifikat, dataset latihan, dan laporan evaluasi.','price':7500000,'revenue':0,'created_by':admin})
        QualityCycleRecord.objects.get_or_create(title='PPEPP Praktikum Sistem Informasi', domain='PRACTICUM', stage='PENETAPAN', period=str(year), defaults={'owner':leader,'status':'ONGOING','standard':'Standar mutu praktikum, kesiapan modul, asisten, jadwal, presensi, dan evaluasi kepuasan.','implementation_summary':'Koordinasi dengan Kelompok Pengampu dan Program Studi.','evaluation_findings':'Belum ada temuan mayor.','corrective_action':'Pemutakhiran modul dan rubrik asesmen.'})
        WorkPlanBudget.objects.get_or_create(year=year, program_name='Penguatan Riset, Inovasi, dan Layanan Profesional Lab SI', defaults={'area':'RESEARCH','budget':30000000,'realization':5000000,'funding_source':fs1,'status':'APPROVED','owner':leader,'approved_by':admin,'notes':'RKAT mencakup riset, publikasi, pelatihan, dan operasional mutu lab.'})
        SOPDocument.objects.get_or_create(code='SOP-LABSI-001', defaults={'title':'SOP Pengelolaan Praktikum, Riset, Pengabdian, dan Layanan Profesional','area':'GOVERNANCE','version':'1.0','status':'APPROVED','owner':leader,'description':'SOP terpadu untuk mendukung pelaksanaan tugas dan wewenang Kepala Laboratorium.'})
        PracticumCourse.objects.get_or_create(course_code='CIS61001', academic_year=f'{year}/{year+1}', study_program='Sistem Informasi', defaults={'course_name':'Desain dan Pengembangan Sistem Informasi','semester':'Ganjil','coordinator':leader,'module_status':'READY','implementation_notes':'Modul praktikum diselaraskan dengan CPL dan CPMK.','evaluation_summary':'Evaluasi dilakukan melalui presensi, rubrik tugas, dan kepuasan mahasiswa.'})
        CurriculumSupport.objects.get_or_create(study_program='Sistem Informasi', curriculum_year=year, contribution_type='MODULE', defaults={'course_name':'Desain dan Pengembangan Sistem Informasi','owner':leader,'status':'SUBMITTED','recommendation':'Penguatan materi industrial-grade information system, DevOps, API, keamanan, dan observability pada kurikulum.'})
        RoadmapItem.objects.get_or_create(title='Roadmap Riset Enterprise Systems dan Smart Laboratory', defaults={'area':'RESEARCH','theme':'Enterprise Systems, Smart Laboratory, RAG, Knowledge Graph','start_year':year,'end_year':year+3,'priority':'STRATEGIC','status':'ONGOING','owner_group':groups[0],'owner':leader,'alignment_policy':'Selaras dengan arah kebijakan FILKOM pada riset digital, inovasi, layanan profesional, dan kolaborasi industri.','expected_outputs':'Publikasi bereputasi, produk digital, layanan konsultasi, dataset, dan kemitraan strategis.'})
        TalentProgram.objects.get_or_create(title='Rekrutmen dan Pembinaan Asisten Riset dan Praktikum Lab SI', period=str(year), defaults={'program_type':'PRACTICUM_ASSISTANT','status':'OPEN','coordinator':leader,'selection_criteria':'IPK, portofolio proyek, kemampuan komunikasi, pemahaman metodologi ilmiah, dan komitmen.','mentoring_plan':'Pembinaan mingguan terkait praktikum, riset, publikasi, dan kompetisi ilmiah.','result_summary':'Program berjalan sebagai pipeline talenta laboratorium.'})
        DigitalChannel.objects.get_or_create(name='Website Laboratorium Sistem Informasi', defaults={'channel_type':'WEBSITE','url':'https://labsi.filkom.ub.ac.id','owner':leader,'audience':'Sivitas akademika, mitra industri, pemerintah, alumni, dan masyarakat umum.','status':'ACTIVE','content_strategy':'Eksposur kegiatan riset, publikasi, pengabdian, layanan, dan prestasi mahasiswa.'})
        SatisfactionSurvey.objects.get_or_create(domain='PROFESSIONAL_SERVICE', period=str(year), respondent_segment='Mitra layanan profesional', defaults={'score':4.50,'sample_size':12,'summary':'Pengguna menilai layanan kepakaran informatif dan aplikatif.','follow_up':'Penyempurnaan SLA, dokumentasi luaran, dan kanal permintaan layanan.','owner':leader})
        PerformanceReport.objects.get_or_create(year=year, title=f'Laporan Kinerja Laboratorium Sistem Informasi {year}', defaults={'report_type':'ANNUAL','prepared_by':leader,'approved_by':admin,'status':'DRAFT','executive_summary':'Ringkasan kinerja praktikum, riset, inovasi, pengabdian, layanan profesional, mutu, kerja sama, aset, dan KPI tahunan.'})
        HeadApproval.objects.get_or_create(title='Pengesahan Roadmap Riset dan Layanan Profesional Lab SI', defaults={'decision_type':'ROADMAP','requester':leader,'approver':admin,'status':'APPROVED','requested_at':date.today(),'decided_at':date.today(),'subject_reference':'Roadmap Riset Enterprise Systems dan Smart Laboratory','rationale':'Roadmap diperlukan sebagai acuan prioritas riset, inovasi, pengabdian, dan layanan profesional.','decision_notes':'Disetujui untuk menjadi acuan operasional tahunan.'})
        self.stdout.write(self.style.SUCCESS('Enterprise demo data created.'))
