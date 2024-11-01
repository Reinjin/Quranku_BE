from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import io
import librosa
from .ml_utils import predict_audio_class, predict_audio_biner  # Import fungsi prediksi dari ml_utils
from models import HistoryBelajar, db
from datetime import datetime

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
    

###UNTUK PREDIKSI ML###

# Maksimal ukuran file dalam byte (5MB = 5 * 1024 * 1024)
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'wav'}

# Fungsi untuk memeriksa ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk memeriksa ukuran file
def file_size_okay(file):
    file.seek(0, 2)  # Pindahkan pointer ke akhir file
    size = file.tell()
    file.seek(0)  # Kembalikan pointer ke awal file
    return size <= MAX_FILE_SIZE

class_names = ['01. alif_fathah', '02. alif_kasroh', '03. alif_dommah', '04. ba_fathah', '05. ba_kasroh', '06. ba_dommah',
               '07. ta_fathah', '08. ta_kasroh', '09. ta_dommah', '10. tsa_fathah', '11. tsa_kasroh', '12. tsa_dommah',
               '13. jim_fathah', '14. jim_kasroh', '15. jim_dommah', '16. hah_fathah', '17. hah_kasroh', '18. hah_dommah',
               '19. kha_fathah', '20. kha_kasroh', '21. kha_dommah', '22. dal_fathah', '23. dal_kasroh', '24. dal_dommah',
               '25. dzal_fathah', '26. dzal_kasroh', '27. dzal_dommah', '28. ra_fathah', '29. ra_kasroh', '30. ra_dommah',
               '31. zay_fathah', '32. zay_kasroh', '33. zay_dommah', '34. sin_fathah', '35. sin_kasroh', '36. sin_dommah',
               '37. shin_fathah', '38. shin_kasroh', '39. shin_dommah', '40. sad_fathah', '41. sad_kasroh', '42. sad_dommah',
               '43. dad_fathah', '44. dad_kasroh', '45. dad_dommah', '46. tah_fathah', '47. tah_kasroh', '48. tah_dommah',
               '49. zah_fathah', '50. zah_kasroh', '51. zah_dommah', '52. ain_fathah', '53. ain_kasroh', '54. ain_dommah',
               '55. ghaiin_fathah', '56. ghaiin_kasroh', '57. ghaiin_dommah', '58. fa_fathah', '59. fa_kasroh', '60. fa_dommah',
               '61. qaf_fathah', '62. qaf_kasroh', '63. qaf_dommah', '64. kaf_fathah', '65. kaf_kasroh', '66. kaf_dommah',
               '67. lam_fathah', '68. lam_kasroh', '69. lam_dommah', '70. mim_fathah', '71. mim_kasroh', '72. mim_dommah',
               '73. nun_fathah', '74. nun_kasroh', '75. nun_dommah', '76. Ha_fathah', '77. Ha_kasroh', '78. Ha_dommah',
               '79. waw_fathah', '80. waw_kasroh', '81. waw_dommah', '82. ya_fathah', '83. ya_kasroh', '84. ya_dommah']

# Daftar huruf hijaiyah arab yang diizinkan
huruf_hijaiyah_arab = [
    'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر',
    'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ',
    'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي'
]

# Daftar kondisi suara yang diizinkan
kondisi_list = ['fathah', 'kasroh', 'dommah']

# Fungsi validasi apakah huruf, kondisi, dan hasil prediksi valid
def validate_input(huruf, kondisi, hasil_prediksi):
    if huruf not in huruf_hijaiyah_arab:
        return False, "Invalid huruf"
    if kondisi not in kondisi_list:
        return False, "Invalid kondisi"
    if hasil_prediksi not in class_names:
        return False, "Invalid hasil_prediksi_diinginkan"
    return True, None

# Endpoint untuk melakukan prediksi audio tanpa menyimpan file
@ml.route('/predict', methods=['POST'])
@jwt_required()  # Memerlukan JWT
def predict():
    try:
        # Dapatkan id user dari JWT
        user_id = get_jwt_identity()

        # Validasi input dari request
        if 'file' not in request.files:
            return jsonify({"msg": "No file part in the request"}), 400
        
        file = request.files['file']
        
        # Cek apakah file telah diunggah
        if file.filename == '':
            return jsonify({"msg": "No file selected"}), 400
        
        # Cek ekstensi dan ukuran file
        if not allowed_file(file.filename):
            return jsonify({"msg": "File type not allowed. Only .wav files are accepted"}), 400
        
        if not file_size_okay(file):
            return jsonify({"msg": "File is too large. Maximum size is 5MB"}), 400
        
        # Ambil data tambahan dari request untuk validasi
        huruf = request.form.get('huruf')
        kondisi = request.form.get('kondisi')  # fathah, kasroh, dhommah
        hasil_prediksi_diinginkan = request.form.get('hasil_prediksi_diinginkan')  # nama kelasnya
        tanggal = request.form.get('tanggal')  # tanggal dari ponsel user (YYYY-MM-DD)
        waktu = request.form.get('waktu')  # waktu dari ponsel user (HH:MM:SS)

        if not all([huruf, kondisi, hasil_prediksi_diinginkan, tanggal, waktu]):
            return jsonify({"msg": "Missing huruf, kondisi, hasil_prediksi_diinginkan, tanggal, or waktu"}), 400

        # Validasi huruf, kondisi, dan hasil_prediksi
        valid, error_msg = validate_input(huruf, kondisi, hasil_prediksi_diinginkan)
        if not valid:
            return jsonify({"msg": error_msg}), 400

        # Validasi format tanggal dan waktu
        try:
            tanggal_obj = datetime.strptime(tanggal, '%Y-%m-%d').date()
            waktu_obj = datetime.strptime(waktu, '%H:%M:%S').time()
        except ValueError:
            return jsonify({"msg": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM:SS for time"}), 400

        # Menggunakan Librosa untuk membaca audio dari file stream (tanpa menyimpannya)
        audio_data = file.read()  # Membaca file sebagai bytes
        audio_stream = io.BytesIO(audio_data)  # Ubah ke BytesIO stream

        # Muat file audio menggunakan librosa
        y, sr = librosa.load(audio_stream, sr=None)  # sr=None menjaga sample rate asli

        # Lakukan prediksi menggunakan fungsi predict_audio_class
        predicted_class = predict_audio_class(y, sr)

        # Bandingkan hasil prediksi dengan hasil prediksi yang diinginkan
        is_correct = "benar" if predicted_class == hasil_prediksi_diinginkan else "kurang"

        # Simpan data history prediksi ke database menggunakan waktu dan tanggal dari client
        history = HistoryBelajar(
            huruf=huruf,
            tanggal=tanggal_obj,
            waktu=waktu_obj,
            kondisi=kondisi,
            hasil=is_correct,
            user_id=user_id
        )

        db.session.add(history)
        db.session.commit()

        # Kembalikan hasil prediksi dan apakah benar atau salah
        return jsonify({
            "result": is_correct
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"msg": "Error during prediction"}), 500
    

# Endpoint untuk melakukan prediksi audio tanpa menyimpan file
@ml.route('/predict_biner', methods=['POST'])
@jwt_required()  # Memerlukan JWT
def predict_biner():
    try:
        # Dapatkan id user dari JWT
        user_id = get_jwt_identity()

        # Validasi input dari request
        if 'file' not in request.files:
            return jsonify({"msg": "No file part in the request"}), 400
        
        file = request.files['file']
        
        # Cek apakah file telah diunggah
        if file.filename == '':
            return jsonify({"msg": "No file selected"}), 400
        
        # Cek ekstensi dan ukuran file
        if not allowed_file(file.filename):
            return jsonify({"msg": "File type not allowed. Only .wav files are accepted"}), 400
        
        if not file_size_okay(file):
            return jsonify({"msg": "File is too large. Maximum size is 5MB"}), 400
        
        # Ambil data tambahan dari request untuk validasi
        huruf = request.form.get('huruf')
        kondisi = request.form.get('kondisi')  # fathah, kasroh, dhommah
        hasil_prediksi_diinginkan = request.form.get('hasil_prediksi_diinginkan')  # nama kelasnya
        tanggal = request.form.get('tanggal')  # tanggal dari ponsel user (YYYY-MM-DD)
        waktu = request.form.get('waktu')  # waktu dari ponsel user (HH:MM:SS)

        if not all([huruf, kondisi, hasil_prediksi_diinginkan, tanggal, waktu]):
            return jsonify({"msg": "Missing huruf, kondisi, hasil_prediksi_diinginkan, tanggal, or waktu"}), 400

        # Validasi huruf, kondisi, dan hasil_prediksi
        valid, error_msg = validate_input(huruf, kondisi, hasil_prediksi_diinginkan)
        if not valid:
            return jsonify({"msg": error_msg}), 400

        # Validasi format tanggal dan waktu
        try:
            tanggal_obj = datetime.strptime(tanggal, '%Y-%m-%d').date()
            waktu_obj = datetime.strptime(waktu, '%H:%M:%S').time()
        except ValueError:
            return jsonify({"msg": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM:SS for time"}), 400

        # Menggunakan Librosa untuk membaca audio dari file stream (tanpa menyimpannya)
        audio_data = file.read()  # Membaca file sebagai bytes
        audio_stream = io.BytesIO(audio_data)  # Ubah ke BytesIO stream

        # Muat file audio menggunakan librosa
        y, sr = librosa.load(audio_stream, sr=None)  # sr=None menjaga sample rate asli

        # Lakukan prediksi menggunakan fungsi predict_audio_class
        predicted_class = predict_audio_biner(y, sr, hasil_prediksi_diinginkan)

        # Bandingkan hasil prediksi dengan hasil prediksi yang diinginkan
        is_correct = "benar" if predicted_class == 1 else "kurang"

        # Simpan data history prediksi ke database menggunakan waktu dan tanggal dari client
        history = HistoryBelajar(
            huruf=huruf,
            tanggal=tanggal_obj,
            waktu=waktu_obj,
            kondisi=kondisi,
            hasil=is_correct,
            user_id=user_id
        )

        db.session.add(history)
        db.session.commit()

        # Kembalikan hasil prediksi dan apakah benar atau salah
        return jsonify({
            "result": is_correct
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"msg": "Error during prediction"}), 500