# app.py

import logging
from flask import Flask
from flask_jwt_extended import JWTManager

from config import Config
from swagger import init_swagger
from routes.auth import auth_bp, JWT_BLOCKLIST
from routes.users import user_bp

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_revoked(_, payload):
    return payload['jti'] in JWT_BLOCKLIST

init_swagger(app)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )
    app.run(debug=True)
