# Flask Markdown Blog Platform

## 🚀 Deskripsi Proyek

Aplikasi manajemen blog berbasis Flask yang memungkinkan publikasi, pengelolaan, dan tampilan konten markdown dengan arsitektur modular dan fungsional.

## 🌟 Fitur Utama

1. **Manajemen Konten**
    
    - Publikasi post markdown dinamis
    - Edit dan hapus post dengan autentikasi

2. **Fungsionalitas**
    
    - Ekstraksi metadata otomatis
    - Rendering markdown ke HTML
    - Penyimpanan dalam database MySQL
	- Manajemen file markdown aman

## 🚦 Cara Instalasi & Penggunaan

### Requirements

- Python 3.8+
- MySQL Server
- Git
### Instalation
1. **Clone Repository**
```bash
git clone https://github.com/fadilsflow/flaskmd.git
cd flaskmd
```
2. **Buat Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
```
3. **Install Dependencies**
```bash
pip install -r requirements.txt
```
4. **Konfigurasi Database**
- Buat database MySQL baru
- Edit `config.py` dengan kredensial database:
```python
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_NAME = 'blog_database'
```
5. Inisialisasi Database
```bash
# Jalankan script SQL untuk membuat tabel
mysql -u your_username -p your_database < db/db.sql
```
6. Run Apps
```bash
python app.py
```
### Membuat Post dengan Markdown
1. Buat file markdown di folder `posts/`
2. Gunakan format metadata YAML:
```yaml
---
title: Judul Postingan
date: 2024-12-19
author: Nama Penulis
readingtime: 5min
tags:
- tag1
- tag2
- tag3
image: /path/to/cover.jpg
---

Markdown Konten ...
```
## 🏗️ Arsitektur Teknis

### Komponen Utama

- **Framework**: Flask
- **Database**: MySQL (PyMySQL)
- **Parsing**:
    - Markdown: markdown2
    - Metadata: PyYAML
- **Fitur Keamanan**:
    - File secure filename
    - Secret key validasi

### Struktur
```
project/
├── app.py           # Aplikasi utama
├── config.py        # Konfigurasi
├── blog/
│   ├── routes.py    # Definisi rute
│   └── models.py    # Logika data
├── posts/           # File markdown
└── db/              # Script database
```
## 🔑 Rute Utama

|Rute|Fungsi|
|---|---|
|`/`|Halaman beranda|
|`/add_blog`|Tambah post baru|
|`/post/<filename>`|Tampilan post spesifik|
|`/manage_blogs`|Manajemen post|
|`/blog/tag/<tag>`|Filter post berdasarkan tag|

## 💾 Struktur Database

**Tabel `posts`**:

- `id`: Identifikasi unik
- `title`: Judul post
- `date`: Tanggal publikasi
- `author`: Penulis
- `tags`: Kategori
- `filename`: Referensi markdown

## 🔒 Keamanan & Validasi

- Secret key untuk manajemen
- Sanitasi input file
- Validasi metadata markdown
- Pembatasan akses admin

## 📊 Teknologi Inti

![Python](https://img.shields.io/badge/Python-3.8+-blue)![Flask](https://img.shields.io/badge/Flask-2.x-green)![MySQL](https://img.shields.io/badge/MySQL-8.x-orange)

## 🤝 Kontribusi

1. Fork repository
2. Buat branch fitur
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request

## 📜 Lisensi

MIT License