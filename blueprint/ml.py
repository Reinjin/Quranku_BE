from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import HistoryBelajar

# Inisialisasi blueprint
ml = Blueprint('ml', __name__)

# Endpoint untuk mengambil history belajar berdasarkan user yang sedang login
@ml.route('/history_belajar', methods=['GET'])
@jwt_required()
def get_history_belajar():
    try:
        # Dapatkan user_id dari token JWT
        user_id = get_jwt_identity()

        # Ambil parameter pagination dari query string
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Validasi parameter pagination
        if page < 1:
            return jsonify({"msg": "Page number must be greater than 0"}), 400
        if per_page < 1:
            return jsonify({"msg": "Per page number must be greater than 0"}), 400

        # Query history belajar sesuai dengan user_id
        histories = HistoryBelajar.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)

        # Ambil data untuk dikembalikan dalam format JSON
        history_list = []
        for history in histories.items:
            history_data = {
                "huruf": history.huruf,
                "tanggal": history.tanggal.strftime('%Y-%m-%d'),
                "waktu": history.waktu.strftime('%H:%M:%S'),
                "kondisi": history.kondisi,
                "hasil": history.hasil
            }
            history_list.append(history_data)

        # Kembalikan data dalam format JSON dengan pagination
        return jsonify({
            "total_items": histories.total,
            "total_pages": histories.pages,
            "current_page": histories.page,
            "per_page": histories.per_page,
            "history_belajar": history_list
        }), 200

    except Exception :
        # Menangani error yang tidak terduga
        return jsonify({"msg": "An unexpected error occurred"}), 500