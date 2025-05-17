# app.py

import os
import logging
import sys
from flask import Flask, redirect
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Optional extras
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# 1) Load environment variables (local .env or host env)
load_dotenv()

# 2) Create Flask application
app = Flask(__name__)

# 3) Configure logging (structured to stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    stream=sys.stdout
)

# 4) Security headers (HSTS, CSP defaults)
Talisman(app, content_security_policy=None)

# 5) Enable CORS (allow all origins by default)
CORS(app)

# 6) Rate limiting (default 200/day, 50/hour)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


# 7) Load configuration from Config class
from config import Config
app.config.from_object(Config)

# 8) Initialize database (create tables if missing)
from CREATE_DB_CODE.tables_creation import init_db
init_db()

# 9) Setup JWT Manager
jwt = JWTManager(app)
from routes.auth import JWT_BLOCKLIST

@jwt.token_in_blocklist_loader
def check_revoked(_, payload):
    return payload['jti'] in JWT_BLOCKLIST

# 10) Swagger UI
from swagger import init_swagger
init_swagger(app)

# 11) Register Blueprints
from routes.auth import auth_bp
from routes.users import user_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')

# 12) Redirect root to Swagger UI
@app.route('/')
def home():
    return redirect('/apidocs', code=302)

# 13) Redirect trailing slash on /apidocs/
@app.route('/apidocs/')
def apidocs_slash():
    return redirect('/apidocs', code=301)

# 14) Health‑check endpoint
@app.route('/health')
def health():
    return {'status': 'ok'}, 200

# 15) Example of per-route rate limit override
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login_rate_limited():
    # delegate to original login
    return auth_bp.view_functions['login']()  # calls the login view

# 16) Entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
