## 1. Cara Setup & Menjalankan Server
1. Clone Repositori (Opsional)
   Jika ini adalah repositori git, clone terlebih dahulu. Jika tidak, pastikan berada di folder proyek.

2. Buat Virtual Environment
   ```bash
   python -m venv .venv
   .venv\Scripts\activate     # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install Dependencies
   ```bash
   pip install Flask PyJWT python-dotenv Flask-SQLAlchemy Werkzeug
   ```
   Atau gunakan requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

4. Konfigurasi Environment
   Buat file .env di root proyek dengan isi:
   ```
   JWT_SECRET=ini-sangatlah-rahasia-saya-kelompok-3-iae-2025
   PORT=5000
   DATABASE_URL=sqlite:///instance/app.db
   ```

5. Jalankan Server
   ```bash
   python app.py
   ```
   Server akan berjalan di http://localhost:5000

## 2. Database
- SQLite digunakan sebagai database default
- Database akan otomatis diinisialisasi saat pertama kali menjalankan server
- File database akan dibuat sesuai DATABASE_URL di .env

## 3. Daftar Endpoint API

### Autentikasi
* **GET /login**
  - Menampilkan halaman login
  - Response: HTML login page

* **POST /auth/login**
  - Login untuk mendapatkan JWT token
  - Request Body: JSON atau Form Data
    ```json
    {
      "email": "user@example.com",
      "password": "password123"
    }
    ```
  - Response: JSON dengan token JWT
    ```json
    {
      "access_token": "eyJ0eXAi..."
    }
    ```

### Items
* **GET /items**
  - Mendapatkan semua items (JSON)
  - Response: Array of items
    ```json
    {
      "items": [
        {"id": 1, "name": "Item 1", "price": 1000},
        {"id": 2, "name": "Item 2", "price": 2000}
      ]
    }
    ```

* **GET /items/view**
  - Menampilkan halaman items
  - Response: HTML items page

* **POST /items/add**
  - Menambah item baru (Admin only)
  - Requires: JWT token with admin role
  - Request Body:
    ```json
    {
      "name": "New Item",
      "price": 1000
    }
    ```

### Profile
* **GET /profile**
  - Melihat profile pengguna
  - Requires: JWT token
  - Response format:
    - JSON jika Accept: application/json atau ?format=json
    - HTML profile page (default)
  - JSON Response:
    ```json
    {
      "profile": {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name",
        "role": "user"
      }
    }
    ```

* **PUT/POST /profile/update**
  - Update profile pengguna
  - Requires: JWT token
  - Request Body:
    ```json
    {
      "name": "New Name"
    }
    ```

### Admin
* **GET /users**
  - Mendapatkan daftar semua users
  - Requires: JWT token with admin role
  - Response: Array of users

## 4. Authentication
- JWT token digunakan untuk autentikasi
- Token dikirim melalui:
  - Header: `Authorization: Bearer <token>`
  - Cookie: `jwt_token=<token>`
- Token expired dalam 15 menit

## 5. Testing dengan cURL

```bash
# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get Items
curl http://localhost:5000/items

# View Profile (JSON)
curl http://localhost:5000/profile \
  -H "Authorization: Bearer <your-token>" \
  -H "Accept: application/json"

# Update Profile
curl -X PUT http://localhost:5000/profile/update \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Name"}'

# Add Item (Admin only)
curl -X POST http://localhost:5000/items/add \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Item","price":1000}'
```