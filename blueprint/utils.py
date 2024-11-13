from flask import Blueprint, request, jsonify
from prayer_times_calculator import PrayerTimesCalculator
from flask_jwt_extended import jwt_required
from geopy.geocoders import Nominatim

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
        city = get_city_name(latitude, longitude)

        # Kembalikan 5 waktu sholat
        return jsonify({
            "City": city,
            "Fajr": times['Fajr'],
            "Dhuhr": times['Dhuhr'],
            "Asr": times['Asr'],
            "Maghrib": times['Maghrib'],
            "Isha": times['Isha']
        }), 200
    except Exception:
        # Menangani error yang tidak terduga
        return jsonify({"message": "An unexpected error occurred while fetching prayer times."}), 500


def get_city_name(latitude, longitude):
            geolocator = Nominatim(user_agent="quranku_app_be")
            location = geolocator.reverse((latitude, longitude), exactly_one=True)
            if location and 'city' in location.raw['address']:
                return location.raw['address']['city']
            elif location and 'town' in location.raw['address']:
                return location.raw['address']['town']
            elif location and 'village' in location.raw['address']:
                return location.raw['address']['village']
            return None