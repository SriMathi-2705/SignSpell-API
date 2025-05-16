#tables_creation.py
from sqlalchemy import (
    Table, MetaData, Column, Integer, DateTime, Boolean,
    BigInteger, String, PrimaryKeyConstraint, func
)

from DB_CONNECTION.config import engine
import logging

metadata = MetaData()
connection = engine.connect()  

try:
    tbl_User = Table(
        'tbl_User', metadata,

        # Primary Key
        Column('lng_User_ID', BigInteger, autoincrement=True),

        # Required User Fields
        Column('str_First_Name', String(100), nullable=False),
        Column('str_Last_Name', String(100), nullable=False),
        Column('str_Full_Name', String(200), nullable=False),
        Column('str_Location',String(50),nullable=False),
        Column('str_Email', String(300), nullable=False),
        Column('str_Password_hash', String, nullable=True),

        # Audit Trail Fields
        Column('lng_Created_By', BigInteger, nullable=False),
        Column('lng_Modified_By', BigInteger, nullable=True),
        Column('lng_Deleted_By', BigInteger, nullable=True),

        Column('dte_Created_Date', DateTime, nullable=False, default=func.now()),
        Column('dte_Modified_Date', DateTime, nullable=True),
        Column('dte_Deleted_Date', DateTime, nullable=True),

        Column('bln_IsActive', Boolean, nullable=False, default=True),
        Column('bln_IsDeleted', Boolean, nullable=False, default=False),

        PrimaryKeyConstraint('lng_User_ID', name='PK_User_ID')
    )

    # Create table if not exists
    metadata.create_all(engine, checkfirst= True)
    print("User Table created successfully.")

except Exception as e:
    logging.exception("Table User Creation Failed")
