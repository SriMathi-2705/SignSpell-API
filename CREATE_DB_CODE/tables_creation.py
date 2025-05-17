# CREATE_DB_CODE/tables_creation.py

import logging
from sqlalchemy import (
    Table, Column, BigInteger, String, DateTime, Boolean,
    PrimaryKeyConstraint, func
)
from DB_CONNECTION.config import engine, metadata

# Define your table
tbl_User = Table(
    'tbl_User', metadata,
    Column('lng_User_ID', BigInteger, autoincrement=True),
    Column('str_First_Name', String(100), nullable=False),
    Column('str_Last_Name',  String(100), nullable=False),
    Column('str_Full_Name',  String(200), nullable=False),
    Column('str_Location',   String(50),  nullable=False),
    Column('str_Email',      String(300), nullable=False),
    Column('str_Password_hash', String,    nullable=True),
    Column('lng_Created_By', BigInteger, nullable=False),
    Column('lng_Modified_By', BigInteger, nullable=True),
    Column('lng_Deleted_By',  BigInteger, nullable=True),
    Column('dte_Created_Date',  DateTime, nullable=False, default=func.now()),
    Column('dte_Modified_Date', DateTime, nullable=True),
    Column('dte_Deleted_Date',  DateTime, nullable=True),
    Column('bln_IsActive',   Boolean, nullable=False, default=True),
    Column('bln_IsDeleted',  Boolean, nullable=False, default=False),
    PrimaryKeyConstraint('lng_User_ID', name='PK_User_ID')
)

def init_db():
    """
    Call this once at application startup (not on every import).
    Creates all tables if they don’t exist.
    """
    try:
        metadata.create_all(engine, checkfirst=True)
        print("✅ Tables created or already exist.")
    except Exception:
        logging.exception("Table creation failed")

# Note: Do NOT call init_db() on import. Call it in your app entrypoint:
#     from CREATE_DB_CODE.tables_creation import init_db
#     init_db()
