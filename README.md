Jika anda ingin menjalankannya pada lokal anda : 

1. aktifkan load_dotenv pada file config.py

2. copy file example.env lalu jadikan namanya .env

3. sesuaikan isi .env dengan keinginan anda

4. anda bisa melakukan setting pada file docker-compose.yaml (jika menggunakan docker compose), anda bisa mencari contoh perintah yang digunakan pada docker.sh

5. anda bisa memenuhi library python anda dengan file requirement.txt terlebih dahulu jika anda ingin menjalankannya langsung

6. lakukan migrasi dengan flask 
	- flask db init
	- flask db migrate -m "initial migrate"
	- flask db upgrade

7. run file app.py


Jika Menginginkan Docker Image nya silahkan pull di 

https://hub.docker.com/r/reinjin/quranku_app

Perintah untuk pull : 

docker pull reinjin/quranku_app