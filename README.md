## 1. Cara Setup & Menjalankan Server
Clone Repositori (Opsional) Jika ini adalah repositori git, clone terlebih dahulu. Jika tidak, pastikan berada di folder proyek.

Buat Virtual Environment.

   ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  venv\Scripts\activate     # Windows
   ```

Install Dependencies Buat file requirements.txt yang berisi:

   ```bash
  Flask
  PyJWT
  python-dotenv
  Flask-CORS
  Flask-SQLAlchemy
  Werkzeug
   ```

Lalu, install menggunakan pip

   ```bash
   pip install -r requirements.txt
   ```

Konfigurasi Environment Buat file bernama .env di direktori root proyek

Jalankan Server (dan Inisialisasi DB) Jalankan aplikasi Flask

## 2. Variabel Environment
1. Wajib membuat file .env di root proyek

2. Ubah env menjadi

  ```bash
  JWT_SECRET=your_jwt_secret_key
  PORT=5000
  DATABASE_URL=sqlite:///app.db
   ```

Jika DATABASE_URL tidak disediakan, aplikasi akan otomatis menggunakan file SQLite bernama app.db

## 3. Daftar Endpoint API

###Autentikasi
* **POST /auth/login**
  Endpoint publik untuk mendapatkan token JWT. Data kredensial akan dicek ke database.

### Items (Marketplace)

* **GET /items**
  Endpoint publik untuk melihat semua item dari database.

### Profil Pengguna

* **PUT /profile/update**
  Endpoint terproteksi (wajib JWT) untuk memperbarui nama pengguna yang sedang login.
  Endpoint ini juga menerima metode **POST**.

## 4. Contoh Pengujian (cURL)
Pastikan server Anda sedang berjalan (python app.py).

* **Langkah 1: Login untuk Mendapatkan Token**
  ```bash
  curl -X POST http://localhost:5000/auth/login -d '{"email":"user1@example.com","password":"pass123"}' -H "Content-Type: application/json"
  ```
* **Langkah 2: Simpan Token ke Variabel**
  ```bash
  export TOKEN=<JWT_TOKEN>
  ```
* **Langkah 3: Akses Endpoint Publik /items**
  ```bash
  curl http://localhost:5000/items
  ```
* **Langkah 4: Akses Endpoint Terproteksi /profile/update (Dengan Token)**
  ```bash
  curl -X PUT http://localhost:5000/profile/update -H "Authorization: Bearer $TOKEN" -d '{"name":"NewName"}' -H "Content-Type: application/json"
  ```
* **Langkah 5: Tes Negatif (Akses /profile/update Tanpa Token)**
  ```bash
  curl -X PUT http://localhost:5000/profile/update -d '{"name":"NewName"}' -H "Content-Type: application/json"
  ```


