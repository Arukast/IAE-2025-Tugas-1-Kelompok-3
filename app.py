import os
import datetime
from flask import Flask, make_response, render_template, request, jsonify
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
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
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
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(None, 1)[1]
        else:
            token = request.cookies.get('jwt_token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # normalize token string (remove quotes or accidental byte-repr)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        token = token.strip().strip('"').strip("'")
        if token.startswith("b'") and token.endswith("'"):
            token = token[2:-1]
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            sub = data.get('sub')
            try:
                user_id = int(sub)
            except (TypeError, ValueError):
                return jsonify({'message': 'Token is invalid!', 'reason': 'Invalid subject type'}), 401
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({"error": "User not found"}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
            # debug info (remove in production)
            # return jsonify({
            #     'message': 'Token is invalid!',
            #     'reason': str(e),
            #     'token_sample': token[:60]
            # }), 401

        return f(current_user, *args, **kwargs)

    return decorated

# Endpoint 1: Login
# Endpoint 1.1: View Login Page
@app.route('/login')
def login():
    return render_template('login.html')

#Endpoint 1.2: Auth Login API
@app.route('/auth/login', methods=['POST'])
def auth():
    # accept JSON or form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    # use the model method (or password_hash) to verify
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    token = jwt.encode(
        {
            'sub': str(user.id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        },
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    # ensure token is a str (PyJWT may return bytes)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    # return token as JSON (no redirect)
    # return token in JSON and set httponly cookie for convenience
    resp = make_response(jsonify({'access_token': token}), 200)
    resp.set_cookie('jwt_token', token, httponly=True, samesite='Lax')
    return resp



#Endpoint 2: Items
# Endpoint 2.1: Get Items (JSON) API
@app.route('/items', methods=['GET'])
def get_items():
    all_items = Item.query.all()

    list_item = [item.to_dict() for item in all_items]
    return jsonify({"items": list_item})

# Endpoint 2.2: View Items (HTML) Page
@app.route('/items/view', methods=['GET'])
def items_view():
    items = Item.query.all()
    return render_template('items.html', items=items)

# Endpoint 3: Profile
#Endpoint 3.1: View Profile Page
@app.route('/profile', methods=['GET'])
@token_required
def view_profile(current_user):
    return render_template('profil.html', user=current_user)

#Endpoint 3.2: Get Profile (JSON) API
@app.route('/profile/update', methods=['PUT', 'POST'])
@token_required
def update_profile(current_user):
    # accept JSON or form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    new_name = data.get('name')
    if not new_name:
        return jsonify({"error": "No valid fields to update ('name')"}), 400

    current_user.name = new_name
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
            
            item1 = Item(name="Lonovo Ligion 5i", price=15000000)
            item2 = Item(name="Ligotech R25", price=750000)
            
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