# models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash
import time


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Tabel untuk menyimpan JWT token yang dihasilkan saat login
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)  # JTI (JWT ID) yang unik

    # Kolom created_at bertipe Integer untuk menyimpan Unix timestamp
    created_at = db.Column(db.Integer, nullable=False, default=lambda: int(time.time()))

    # Kolom id_user sebagai foreign key yang mereferensi ke User.id
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relasi ke model User
    user = db.relationship('User', backref=db.backref('token_blocklist', lazy=True))


class HistoryBelajar(db.Model):
    __tablename__ = 'history_belajar'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Kolom huruf
    huruf = db.Column(db.String(10), nullable=False)
    
    # Kolom tanggal dan waktu
    tanggal = db.Column(db.Date, nullable=False)
    waktu = db.Column(db.Time, nullable=False)
    
    # Kolom kondisi (fathah, kasroh, dhommah)
    kondisi = db.Column(Enum('fathah', 'kasroh', 'dhommah', name='kondisi_enum'), nullable=False)
    
    # Kolom hasil (kurang, benar)
    hasil = db.Column(Enum('kurang', 'benar', name='hasil_enum'), nullable=False)
    
    # Foreign key untuk user_id yang merujuk ke tabel User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relasi ke model User
    user = db.relationship('User', backref=db.backref('history_belajar', lazy=True))