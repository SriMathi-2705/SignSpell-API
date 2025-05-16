from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")  # read secret key from .env
    JWT_SECRET_KEY = SECRET_KEY

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    SWAGGER = {
        'title': 'SIGN SPELL API',
        'uiversion': 3
    }
