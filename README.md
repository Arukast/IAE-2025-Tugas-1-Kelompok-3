## 1. Cara Setup & Menjalankan Server

Clone Repositori (Opsional) Jika ini adalah repositori git, clone terlebih dahulu. Jika tidak, pastikan berada di folder proyek.
Buat Virtual Environment Sangat disarankan untuk menggunakan virtual environment
Install Dependencies Buat file requirements.txt yang berisi:
---
> Flask
> PyJWT
> Python-dotenv
> Flask-CORS
> Flask-SQLAlchemy
> Werkzeug
Lalu, install menggunakan pip
Konfigurasi Environment Buat file bernama .env di direktori root proyek
Jalankan Server (dan Inisialisasi DB) Jalankan aplikasi Flask

## 2. Variabel Environment

Wajib membuat file .env di root proyek
Ubah env menjadi
> JWT_SECRET=your_jwt_secret_key
> PORT=5000
> DATABASE_URL=sqlite:///app.db
Jika DATABASE_URL tidak disediakan, aplikasi akan otomatis menggunakan file SQLite bernama app.db

## 3. Daftar Endpoint API

a. Autentikasi
- POST /auth/login
- Endpoint publik untuk mendapatkan token JWT. Data kredensial dicek ke database.

b. Items (Marketplace)
- GET /items
- Endpoint publik untuk melihat semua item dari database.

c. Profil Pengguna
- PUT /profile/update
- Endpoint terproteksi (wajib JWT) untuk memperbarui nama pengguna yang sedang login. Juga menerima metode POST

## 4. Contoh Pengujian (cURL)
Pastikan server Anda sedang berjalan (python app.py).
---
> Login untuk Mendapatkan Token
> Simpan Token ke Variabel
> Akses Endpoint Publik /items
> Akses Endpoint Terproteksi /profile/update (Dengan Token)
> Tes Negatif (Akses /profile/update Tanpa Token)
