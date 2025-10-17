import os
import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import jwt
from functools import wraps


load_dotenv()

# Membaca variabel dari .env
jwt_secret = os.getenv('JWT_SECRET')
if not jwt_secret:
    raise RuntimeError("JWT_SECRET tidak ditemukan di (.env)")

# Inisialisasi Aplikasi Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = jwt_secret
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Inisialisasi Database
db = SQLAlchemy(app)
PORT = int(os.environ.get('PORT', 5000))

# MODEL DATABASE (ORM)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Fungsi helper untuk mengubah objek menjadi dictionary
    def to_dict(self):
        return {"id": self.id, "email": self.email, "name": self.name}
    
#Fungsi helper mencari user
def find_user_by_email(email):
    for user in User:
        if user['email'] == email:
            return user
    return None

def find_user_by_id(user_id):
    for user in User:
        if user['id'] == user_id:
            return user.copy() 
    return None


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    
    # Fungsi helper untuk mengubah objek menjadi dictionary
    def to_dict(self):
        return {"id": self.id, "name": self.name, "price": self.price}

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt_token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(email=data['sub']).first()
            if not current_user:
                return jsonify({"error": "User not found"}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

#Endpoint 1: login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data.get('email')
    password = data.get('password')
    user = find_user_by_email(email)
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    payload = {
        'sub': user['id'], # Subject (ID unik user)
        'email': user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15) # Waktu kedaluwarsa 15 menit
    }

    token = jwt.encode(
        payload,
        app.config['JWT_SECRET'],
        algorithm='HS256'
    )

    return jsonify({'access_token': token}), 200

#Endpoint 2: Items
@app.route('/items', methods=['GET'])
def get_items():
    all_items = Item.query.all()

    list_item = [item.to_dict() for item in all_items]
    return jsonify({"items": list_item})


#Endpoint 3: Profile
@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body cannot be empty"}), 400
        
    updated = False
    if 'name' in data and data['name']:
        current_user.name = data['name']
        updated = True
    
    if not updated:
        return jsonify({"error": "No valid fields to update ('name')"}), 400

    db.session.commit()
    
    print(f"INFO: Profil untuk {current_user.email} berhasil diperbarui.")
    return jsonify({
        "message": "Profile updated successfully",
        "profile": current_user.to_dict()
    })

# FUNGSI UNTUK INISIALISASI DATABASE
def init_db():
    with app.app_context():
        db.create_all()
        # Cek jika user demo belum ada, maka buat
        if not User.query.filter_by(email="user1@example.com").first():
            print("Creating demo user and items...")
            demo_user = User(email="user1@example.com", name="User Satu")
            demo_user.set_password("pass123")
            
            item1 = Item(name="Laptop Pro", price=15000000)
            item2 = Item(name="Mouse Gaming", price=750000)
            
            db.session.add(demo_user)
            db.session.add(item1)
            db.session.add(item2)
            
            db.session.commit()
            print("Database initialized with demo data.")
        else:
            print("Database already contains data.")

if __name__ == '__main__':
    # Panggil fungsi inisialisasi saat server pertama kali dijalankan
    init_db()
    app.run(debug=True, port=PORT)