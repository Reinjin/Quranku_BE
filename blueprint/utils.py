from flask import Blueprint, request, jsonify
from prayer_times_calculator import PrayerTimesCalculator
from flask_jwt_extended import jwt_required

# Inisialisasi blueprint utils
utils = Blueprint('utils', __name__)

# Endpoint untuk mendapatkan waktu sholat berdasarkan lokasi
@utils.route('/prayer_times', methods=['POST'])
@jwt_required()
def prayer_times():
    try:
        data = request.get_json()

        # Ambil latitude, longitude, dan timezone dari input user
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        hari = data.get('date')

        if not latitude or not longitude:
            return jsonify({"message": "Please provide both latitude and longitude."}), 400

        # Metode perhitungan (contoh: Muslim World League)
        calculation_method = 'kemenag'

        # Hitung waktu sholat untuk hari ini
        ptc = PrayerTimesCalculator(
            latitude=latitude,
            longitude=longitude,
            calculation_method=calculation_method,
            date=hari
        )

        times = ptc.fetch_prayer_times()

        # Kembalikan 5 waktu sholat
        return jsonify({
            "Fajr": times['Fajr'],
            "Dhuhr": times['Dhuhr'],
            "Asr": times['Asr'],
            "Maghrib": times['Maghrib'],
            "Isha": times['Isha']
        }), 200
    except Exception:
        # Menangani error yang tidak terduga
        return jsonify({"message": "An unexpected error occurred while fetching prayer times."}), 500
