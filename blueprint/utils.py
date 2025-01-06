from flask import Blueprint, request, jsonify
# from prayer_times_calculator import PrayerTimesCalculator
from flask_jwt_extended import jwt_required
# from geopy.geocoders import Nominatim
import requests


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

        if not latitude or not longitude or not hari:
            return jsonify({"message": "Please provide both latitude, longitude, and date."}), 400

        # Get prayer times
        prayer_times = get_prayer_times(
        date=hari,
        latitude=latitude,
        longitude=longitude
        )

        times = prayer_times["data"]["timings"]
        
        # Kembalikan 5 waktu sholat yang diminta
        return jsonify({
            "fajr": times['Fajr'],
            "dhuhr": times['Dhuhr'],
            "asr": times['Asr'],
            "maghrib": times['Maghrib'],
            "isha": times['Isha']
        }), 200
    except Exception:
        # Menangani error yang tidak terduga
        return jsonify({"message": "An unexpected error occurred while fetching prayer times."}), 500

@utils.route('/city_location', methods=['POST'])
@jwt_required()
def city_location():
    try:
        data = request.get_json()

        # Ambil latitude, longitude dari input user
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not latitude or not longitude:
            return jsonify({"message": "Please provide both latitude and longitude."}), 400

        city = get_location_info(latitude, longitude)
        
        # Kembalikan nama kota
        return jsonify({
            "city": city[0]['name']
        }), 200
    except Exception:
        # Menangani error yang tidak terduga
        return jsonify({"message": "An unexpected error occurred while fetching city location."}), 500
    
# def get_city_name(latitude, longitude):
#             geolocator = Nominatim(user_agent="quranku_app_be")
#             location = geolocator.reverse((latitude, longitude), exactly_one=True)
#             if location and 'city' in location.raw['address']:
#                 return location.raw['address']['city']
#             elif location and 'town' in location.raw['address']:
#                 return location.raw['address']['town']
#             elif location and 'village' in location.raw['address']:
#                 return location.raw['address']['village']
#             return None

def get_location_info(lat, lon, limit=1):
    """
    Get location information from OpenWeatherMap Geocoding API
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
        limit (int): Number of locations to return (default: 5)
    
    Returns:
        dict: Location information if successful, None if failed
    """
    # API configuration
    API_KEY = "86b1da43833a27764f811389fcb8d3c4"
    BASE_URL = "http://api.openweathermap.org/geo/1.0/reverse"
    
    # Parameters for the request
    params = {
        "lat": lat,
        "lon": lon,
        "limit": limit,
        "appid": API_KEY
    }
    
    try:
        # Make the request
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Return the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location data: {e}")
        return None

def get_prayer_times(date, latitude, longitude, method=20):
    """
    Get prayer times from Aladhan API
    
    Args:
        date (str): Date in DD-MM-YYYY format
        latitude (int): Latitude of location
        longitude (int): Longitude of location
        method (int): Calculation method (default: 20)
        
    Returns:
        dict: Prayer times data
    """
    # Base URL
    base_url = "https://api.aladhan.com/v1/timings"
    
    # Create the full URL with path parameter
    url = f"{base_url}/{date}"
    
    # Query parameters
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "method": method
    }
    
    try:
        # Make the GET request
        response = requests.get(url, params=params)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching prayer times: {e}")
        return None