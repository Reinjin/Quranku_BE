from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User

# Inisialisasi blueprint user
user = Blueprint('user', __name__)

# Endpoint untuk mengambil profil user
@user.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        # Dapatkan user_id dari token yang digunakan
        user_id = get_jwt_identity()
        
        # Validasi jika user_id tidak ditemukan
        if not user_id:
            return jsonify({"message": "User identity not found"}), 400
        
        # Cari user berdasarkan user_id
        user = User.query.get(user_id)
        
        # Jika user tidak ditemukan
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Mengembalikan data profil user: full_name dan email
        return jsonify({
            "full_name": user.full_name,
            "email": user.email
        }), 200
    except Exception:
        # Menangani error yang tidak terduga
        return jsonify({"message": "An error occurred while fetching the profile"}), 500
