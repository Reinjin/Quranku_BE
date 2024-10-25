### PERINTAH UNTUK CONTAINER MYSQL ###
# pull mysql image
docker pull mysql
# create mysql container
docker container create --name mysql -e MYSQL_ROOT_PASSWORD=178292219 -e MYSQL_DATABASE=quranku_app -p 3306:3306 mysql
# start mysql container
docker container start mysql

### PERINTAH UNTUK BUILD APP ###
docker build -t reinjin/quranku_app .

### PEINTAH UNTUK MEMBUAT DAN MENJALANKAN CONTAINER LOKAL ###
docker container create --name quranku_app -e SECRET_KEY=your_secret_key -e JWT_SECRET_KEY=your_JWT_secretkey -e DATABASE_URL=your_database_connection_string -p 5003:5003 reinjin/quranku_app:latest

### PERINTAH UNTUK MENJALANKAN DOCKER-COMPOSE.YAML ###
docker-compose up -d
docker-compose down 