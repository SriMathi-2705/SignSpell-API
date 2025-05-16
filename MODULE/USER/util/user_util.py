import re
import logging
from sqlalchemy import select
import pyaes  # type: ignore
import binascii
from DB_CONNECTION.helper_file import keypass, iv
import socket

RESERVED_DOMAINS = {
    'example.com', 'example.net', 'example.org', 'localhost', 'test', 'invalid'
}

def validate_email_format(email):
    try:
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(email_regex, email))
    except Exception as e:
        logging.exception(f"validate_email_format error: {e}")
        return False

def validate_email_domain(email: str) -> bool:
    try:
        # Validate email format first
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            return False

        domain = email.split('@')[-1].lower()
        if domain in RESERVED_DOMAINS:
            return False

        # Check domain DNS resolution
        socket.gethostbyname(domain)
        return True
    except Exception as e:
        logging.exception(f"validate_email_domain error: {e}")
        return False


COMMON_WEAK_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123",
    "111111", "123123", "admin", "letmein", "welcome"
}

def validate_password(password: str) -> tuple[bool, str]:
    try:
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        
        if password.lower() in COMMON_WEAK_PASSWORDS:
            return False, "Password is too common. Choose a stronger password."
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must include at least one uppercase letter."
        
        if not re.search(r"[a-z]", password):
            return False, "Password must include at least one lowercase letter."
        
        if not re.search(r"\d", password):
            return False, "Password must include at least one digit."
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must include at least one special character."
        
        return True, ""
    except Exception as e:
        logging.exception(f"validate_password error: {e}")
        return False, "Password validation error."

def check_unique_value(table, column: str, value, connection):
    try:
        name_check_stmt = (
            select(table.c[column])
            .where(
                (table.c[column] == value) &
                (table.c.bln_IsDeleted != True)
            )
        )
        name_check_data = connection.execute(name_check_stmt).fetchone()
        return bool(name_check_data)
    except Exception as e:
        logging.exception(f"check_unique_value error: {e}")
        return False

def encrypt_password(password: str):
    try:
        plaintext = password
        aes = pyaes.AESModeOfOperationCTR(keypass, pyaes.Counter(iv))
        ciphertext = aes.encrypt(plaintext)
        encrypted = binascii.hexlify(ciphertext).decode("utf-8")
        return encrypted
    except Exception as e:
        logging.exception(f"encrypt_password error: {e}")
        return None
