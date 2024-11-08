# app.py

from flask import Flask, jsonify
from models import db
from blueprint.auth import auth
from blueprint.user import user
from blueprint.utils import utils
from blueprint.ml import ml
from flask_jwt_extended import JWTManager
from config import Config
from flask_migrate import Migrate
from models import TokenBlocklist

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)  # Tambahkan migrasi

jwt = JWTManager(app)

# Cek apakah token sudah di-blacklist
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None

# Custom handler untuk 404 Not Found
@app.errorhandler(404)
def not_found(error):
    return jsonify({"msg": "Endpoint not found"}), 404

# Custom handler untuk 500 Internal Server Error
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"msg": "An internal server error occurred"}), 500

# Register blueprint
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(utils, url_prefix='/utils')
app.register_blueprint(ml, url_prefix='/ml')

@app.route('/')
def home():
    return "Hello, This is Quranku app <br> This is just BackEnd Application, you can access from mobile app" 

if __name__ == '__main__': 
    app.run(port=5003)