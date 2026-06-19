# Lab SI ERIMP — Enterprise Research and Innovation Management Platform

Platform Django industrial-grade untuk mengelola Laboratorium Sistem Informasi: keanggotaan dosen/mahasiswa, riset, inovasi, pengabdian, layanan profesional, praktikum, talenta, kurikulum, kerja sama, aset, KPI, PPEPP, RKAT, SOP, kepuasan pengguna, laporan kinerja, knowledge graph, dan Chatbot RAG berbasis data internal.

## Revisi Utama Versi Ini

- UI CRUD ditingkatkan: aksi **Detail, Edit, Hapus** ditampilkan sebagai button konsisten di seluruh tabel.
- Sidebar lebih rapi, responsif, dan dikelompokkan berdasarkan fungsi Kepala Laboratorium.
- Logo **Lab Sistem Informasi** ditambahkan pada login dan sidebar.
- Modul **Layanan Profesional** ditambahkan untuk mendata layanan kepakaran dosen/mahasiswa kepada pihak internal/eksternal.
- Layanan profesional mendukung skema **gratis, berbayar, dan hybrid**, lengkap dengan koordinator, pakar, mitra, pemohon, harga, pendapatan, luaran, status, dan skor kepuasan.
- Modul tata kelola Kepala Laboratorium ditambahkan:
  - Siklus PPEPP Mutu
  - Rencana Kerja dan Anggaran Tahunan/RKAT
  - SOP dan Tata Laksana
  - Manajemen Praktikum
  - Dukungan Kurikulum
  - Roadmap Riset, Inovasi, Pengabdian, dan Layanan Profesional
  - Rekrutmen dan Pembinaan Talenta/Asisten/Kompetisi
  - Kanal Komunikasi Digital
  - Monitoring Kepuasan Pengguna
  - Laporan Kinerja Laboratorium
  - Otorisasi Kepala Laboratorium
- Knowledge Graph tetap berbasis search dan kini mengindeks layanan profesional, PPEPP, SOP, dan roadmap.
- Chatbot RAG diperluas agar membaca seluruh modul baru, termasuk layanan, SOP, RKAT, PPEPP, praktikum, kurikulum, talenta, kepuasan, laporan, dan otorisasi.
- Admin tetap dapat melakukan CRUD user via UI: tambah user, detail, edit, reset password, hapus.
- User biasa tetap dapat mengupdate profil dan informasi keanggotaannya sendiri melalui **Profil Saya**.

## Modul Utama

1. Keanggotaan dosen/mahasiswa
2. Manajemen user
3. Kelompok riset
4. Kegiatan laboratorium
5. Penelitian
6. Pengabdian kepada masyarakat
7. Publikasi
8. Dataset
9. Source code repository
10. Layanan profesional
11. Mitra CRM
12. MoU/MoA/IA/NDA
13. Praktikum
14. Dukungan kurikulum
15. Rekrutmen dan pembinaan talenta
16. PPEPP mutu
17. RKAT
18. SOP
19. Aset
20. Booking ruang
21. KPI
22. Kepuasan pengguna
23. Laporan kinerja
24. Otorisasi Kepala Lab
25. Knowledge Graph
26. Chatbot RAG

## Menjalankan di Windows CMD

1. Extract ZIP.
2. Buka CMD di folder project.
3. Jalankan:

```cmd
run_local.bat
```

Script akan membuat virtual environment, menginstal dependency, menjalankan migrasi, membuat data awal, dan menjalankan server.

Login awal:

```text
Username: admin
Password: ChangeMe123!
```

Akses:

```text
http://127.0.0.1:8000
```

## Menjalankan Manual

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py bootstrap_labms
python manage.py bootstrap_enterprise
python manage.py runserver
```

## Environment Variable untuk Lokal

Isi `.env`:

```env
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=127.0.0.1,localhost,.vercel.app
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000,https://*.vercel.app
```

## Environment Variable untuk Vercel + Neon

```env
SECRET_KEY=<buat-secret-key-kuat>
DEBUG=False
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DB?sslmode=require
ALLOWED_HOSTS=.vercel.app,domain-anda.ac.id
CSRF_TRUSTED_ORIGINS=https://*.vercel.app,https://domain-anda.ac.id
```

## Catatan Knowledge Graph

Knowledge graph menggunakan Cytoscape.js dari CDN jsDelivr. Halaman `/enterprise/knowledge-graph/` sengaja menampilkan canvas kosong saat belum ada kata kunci agar graph tetap representatif, ringan, dan tidak membanjiri pengguna dengan seluruh database.

Contoh query:

```text
Pelatihan
SOP
PPEPP
Roadmap
AI
Business Process Management
RKAT
Asisten Praktikum
```

## Catatan Chatbot RAG

Chatbot RAG berjalan tanpa API eksternal. Retrieval dilakukan dari database internal dengan tokenisasi, stopword removal, pembobotan judul, pencocokan frasa, ranking skor relevansi, filter modul, dan sumber yang dapat diklik.

Contoh pertanyaan:

```text
Layanan profesional berbayar apa saja?
SOP apa yang sudah disetujui?
Bagaimana PPEPP praktikum tahun ini?
Siapa anggota yang ahli AI?
Roadmap riset apa yang strategis?
Apa saja laporan kinerja laboratorium?
```

## Checklist Validasi

Sebelum deployment:

```cmd
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
```

Pastikan halaman berikut dapat dibuka:

- `/`
- `/accounts/users/`
- `/memberships/`
- `/enterprise/`
- `/enterprise/professional-services/`
- `/enterprise/quality-cycle/`
- `/enterprise/workplans/`
- `/enterprise/sop/`
- `/enterprise/practicums/`
- `/enterprise/curriculum-support/`
- `/enterprise/roadmaps/`
- `/enterprise/talent-programs/`
- `/enterprise/digital-channels/`
- `/enterprise/satisfaction-surveys/`
- `/enterprise/performance-reports/`
- `/enterprise/head-approvals/`
- `/enterprise/knowledge-graph/?q=Pelatihan`
- `/enterprise/rag-chatbot/`
- `/admin/`
