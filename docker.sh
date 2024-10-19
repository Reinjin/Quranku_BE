# pull mysql image
docker pull mysql

# create mysql container
docker container create --name mysql -e MYSQL_ROOT_PASSWORD=178292219 -e MYSQL_DATABASE=quranku_app -p 3306:3306 mysql

# start mysql container
docker container start mysql