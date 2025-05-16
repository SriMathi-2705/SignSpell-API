from datetime import timedelta
import secrets

class Config:
    # Generate a strong 256-bit secret key
    SECRET_KEY = secrets.token_urlsafe(64)  # 64 chars ~ 384 bits
    JWT_SECRET_KEY = SECRET_KEY

    # Token expiry settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Swagger configuration
    SWAGGER = {
        'title': 'SIGN SPELL API',
        'uiversion': 3
    }
