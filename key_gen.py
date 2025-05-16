import secrets
SECRET_KEY = secrets.token_urlsafe(64)  # 64 chars ~ 384 bits
print(SECRET_KEY)