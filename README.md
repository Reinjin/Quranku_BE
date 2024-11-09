# Quranku Backend API

Backend service untuk aplikasi Quranku dengan fitur Machine Learning untuk klasifikasi Huruf Hijaiyah.


## Cara Menjalankan Aplikasi Secara Lokal

### 1. Konfigurasi Environment
- Aktifkan `load_dotenv` pada file `config.py`
- Salin `example.env` menjadi `.env`
- Sesuaikan variabel pada file `.env`:
  ```
  SECRET_KEY=your_secret_key
  JWT_SECRET_KEY=your_jwt_secret_key
  DATABASE_URL=mysql+pymysql://username:password@host:port/database_name
  ```

### 2. Instalasi Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
Jalankan perintah migrasi database:
```bash
flask db init
flask db migrate -m "initial migrate"
flask db upgrade
```

### 4. Persiapan Model Machine Learning
1. Buat folder `model` di dalam folder `blueprint`
2. Masukkan model-model ML yang dibutuhkan ke dalam folder tersebut

#### Model yang Tersedia
Anda dapat menggunakan salah satu atau semua model berikut:

1. **CNN 84 Class**
   - Repository: [Quranku_ML](https://github.com/Reinjin/Quranku_ML)
   - Fungsi: Klasifikasi 84 kelas Huruf Hijaiyah

2. **CNN Biner Classification**
   - Repository: [Quranku_ML_Biner](https://github.com/Reinjin/Quranku_ML_Biner)
   - Fungsi: Klasifikasi biner Huruf Hijaiyah

3. **SVM OneClass**
   - Repository: [Quranku_ML_OneClassSVM](https://github.com/Reinjin/Quranku_ML_OneClassSVM)
   - Fungsi: Klasifikasi one-class menggunakan SVM
  
(Jika anda tidak memasukkan salah satu modelnya maka anda tidak bisa menggunakan endpoint untuk prediksi modelnya)

### 5. Menjalankan Aplikasi
```bash
python app.py
```

## Menggunakan Docker

### Menggunakan Docker Compose
1. Sesuaikan konfigurasi pada file `docker-compose.yaml`
2. Lihat contoh perintah docker pada file `docker.sh`

### Menggunakan Docker Image
[Quranku_app Docker Hub](https://hub.docker.com/repository/docker/reinjin/quranku_app/general)  
Pull image dari Docker Hub:
```bash
docker pull reinjin/quranku_app:v2.1
```

Jalankan container:
```bash
docker run -d \
  -e SECRET_KEY=your_secret_key \
  -e JWT_SECRET_KEY=your_jwt_secret_key \
  -e DATABASE_URL=your_database_url \
  reinjin/quranku_app:v2.1
```
