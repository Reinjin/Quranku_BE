# faker.py

from models import User, db, HistoryBelajar
from faker import Faker
from app import app
import random

fake = Faker()

def generate_fake_users(n):
    with app.app_context():
        for _ in range(n):
            full_name = fake.name()
            email = fake.email()
            password = "Password123"
            user = User(full_name=full_name, email=email)
            user.set_password(password)
            db.session.add(user)
        db.session.commit()

def generate_fake_users11(n=1):
    with app.app_context():
        for _ in range(n):
            full_name = "Fawwaz Ijlal Muqsith"
            email = "fawwazijlalmuqsith@gmail.com"
            password = "Password123"
            user = User(full_name=full_name, email=email)
            user.set_password(password)
            db.session.add(user)
        db.session.commit()

def generate_fake_history_belajar():
    # Daftar huruf yang akan digunakan secara acak
    huruf_list = ['ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي']

    # Daftar kondisi dan hasil
    kondisi_list = ['fathah', 'kasroh', 'dommah']
    hasil_list = ['kurang', 'benar']

    with app.app_context():
        # Membuat data faker untuk setiap user (id 1-10)
        for user_id in range(1, 12):
            for _ in range(100):  # Membuat 10 riwayat untuk setiap user
                huruf = random.choice(huruf_list)  # Huruf acak
                tanggal = fake.date_this_year()  # Tanggal acak dalam tahun ini
                waktu = fake.time()  # Waktu acak
                kondisi = random.choice(kondisi_list)  # Kondisi acak (fathah, kasroh, dhommah)
                hasil = random.choice(hasil_list)  # Hasil acak (kurang, benar)
                
                # Buat objek history_belajar
                history = HistoryBelajar(
                    huruf=huruf,
                    tanggal=tanggal,
                    waktu=waktu,
                    kondisi=kondisi,
                    hasil=hasil,
                    user_id=user_id  # Referensi ke user dengan id tertentu
                )

                # Simpan ke database
                db.session.add(history)

        # Commit semua perubahan ke database
        db.session.commit()

if __name__ == "__main__":
    generate_fake_users(10)
    generate_fake_users11()
    generate_fake_history_belajar()
