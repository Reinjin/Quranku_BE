
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, JWTManager, get_jwt_identity
from models import User, db, TokenBlocklist
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import re  # Library untuk regex

auth = Blueprint('auth', __name__)

# Register
@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Ambil full_name, email, dan password
        full_name = data.get('full_name')
        email = data.get('email')
        password = data.get('password')

        # Cek apakah data full_name, email, dan password ada
        if not full_name:
            return jsonify({"msg": "Full name is required"}), 400
        if not email:
            return jsonify({"msg": "Email is required"}), 400
        if not password:
            return jsonify({"msg": "Password is required"}), 400

        email_lower = email.lower()  # Simpan email dalam lowercase

        # Validasi email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not email or not re.match(email_regex, email):
            return jsonify({"msg": "Email format is invalid"}), 400
        if len(email) < 5 or len(email) > 90:
            return jsonify({"msg": "Email must be between 5 and 90 characters"}), 400

        # Validasi password
        password_regex = r'^(?=.*[A-Z])(?=.*\d).{8,90}$'  # Huruf besar dan angka, panjang minimal 8 dan maksimal 90
        if not password or not re.match(password_regex, password):
            return jsonify({"msg": "Password must contain at least one uppercase letter, one number, and be 8-90 characters long"}), 400

        # Cek apakah email sudah terdaftar
        if User.query.filter_by(email=email).first():
            return jsonify({"msg": "Email already registered"}), 400

        # Menambahkan user baru
        new_user = User(full_name=full_name, email=email_lower)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "User registered successfully"}), 201

    except KeyError:
        # Jika data yang diperlukan tidak ditemukan dalam request
        return jsonify({"msg": "Missing required fields in request"}), 400

    except Exception:
        # Menangani error yang tidak terduga
        return jsonify({"msg": "An error occurred during registration"}), 500

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email:
            return jsonify({"msg": "Email is required"}), 400
        if not password:
            return jsonify({"msg": "Password is required"}), 400

        email_lower = email.lower()  # Simpan email dalam lowercase

        # Validasi format email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email_lower) or len(email_lower) < 5 or len(email_lower) > 90:
            return jsonify({"msg": "Invalid email format. Email must be between 5 and 90 characters long"}), 400

        # Validasi format password
        password_regex = r'^(?=.*[A-Z])(?=.*\d).{8,90}$'  # Minimal 1 huruf besar, 1 angka, panjang 8-90 karakter
        if not re.match(password_regex, password):
            return jsonify({"msg": "Password must contain at least one uppercase letter, one number, and be 8-90 characters long"}), 400

        # Cari user berdasarkan email
        user = User.query.filter_by(email=email_lower).first()
        if not user or not user.check_password(password):
            return jsonify({"msg": "Bad email or password"}), 401

        # Buat JWT token
        access_token = create_access_token(identity=user.id, expires_delta=False)

        return jsonify(access_token=access_token), 200

    except KeyError:
        # Jika data yang diperlukan tidak ditemukan dalam request
        return jsonify({"msg": "Missing required fields in request"}), 400

    except Exception :
        # Menangani error yang tidak terduga
        return jsonify({"msg": "An error occurred during login"}), 500

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # Cek apakah JTI (JWT ID) ada di dalam token
        jti = get_jwt().get('jti', None)
        if not jti:
            return jsonify({"msg": "Eror from token"}), 400

        # Cek apakah user_id ada di dalam token
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"msg": "Eror from token"}), 400

        # Simpan JTI ke dalam TokenBlocklist dengan id_user yang terkait
        token = TokenBlocklist(jti=jti, id_user=user_id)
        db.session.add(token)
        db.session.commit()

        return jsonify({"msg": "Successfully logged out"}), 200

    except Exception :
        # Menangani error lain yang mungkin terjadi
        return jsonify({"msg": "An error occurred during logout"}), 500
