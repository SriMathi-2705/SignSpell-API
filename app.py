# app.py

import os
import logging
from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_cors import CORS

# 1) Load .env (for local dev) and Render env vars automatically
load_dotenv()

# 2) Create the Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)

# 3) Load config from Config class (reads SECRET_KEY, JWT settings, etc.)
from config import Config
app.config.from_object(Config)

# 4) Initialize your database (creates tables if they don't exist)
from CREATE_DB_CODE.tables_creation import init_db
init_db()

# 5) Setup JWT
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_revoked(_, payload):
    return payload['jti'] in JWT_BLOCKLIST

# 6) Swagger UI (for testing only—automatically at /apidocs/)
from swagger import init_swagger
init_swagger(app)

# 7) Register your Blueprints
from routes.auth import auth_bp, JWT_BLOCKLIST
from routes.users import user_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')

from flask import redirect

@app.route('/')
def home():
    return redirect('/apidocs', code=302)


# 8) Entry point
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )

    # Use PORT from env (Render sets this), default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
