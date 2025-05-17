# MODULE/USER/service/user_service.py

import logging
from datetime import datetime
from sqlalchemy import insert, update, select
from sqlalchemy.exc import SQLAlchemyError

from DB_CONNECTION.config import engine
from CREATE_DB_CODE.tables_creation import tbl_User
from MODULE.USER.util.user_util import (
    validate_email_domain,
    validate_password,
    check_unique_value,
    encrypt_password
)

class User:

    @staticmethod
    def save_user_service(data: dict) -> dict:
        try:
            # 1) Required fields
            required = ['str_Email', 'str_First_Name', 'str_Last_Name', 'str_Location', 'str_Password', 'User_ID']
            missing = [f for f in required if not data.get(f)]
            if missing:
                return {'ErrorCode': 9997, 'Message': f'Missing fields: {missing}'}

            # 2) Validate email & password
            if not validate_email_domain(data['str_Email']):
                return {'ErrorCode': 9991, 'Message': 'Invalid or unreachable email domain.'}
            pwd_ok, pwd_msg = validate_password(data['str_Password'])
            if not pwd_ok:
                return {'ErrorCode': 9991, 'Message': pwd_msg}

            with engine.connect() as conn:
                # 3) Check uniqueness
                if check_unique_value(tbl_User, 'str_Email', data['str_Email'], conn):
                    return {'ErrorCode': 9997, 'Message': 'Email already exists'}

                # 4) Encrypt password
                encrypted = encrypt_password(data['str_Password'])
                if not encrypted:
                    return {'ErrorCode': 9992, 'Message': 'Password encryption failed.'}

                # 5) Insert record
                user_rec = {
                    'str_First_Name':    data['str_First_Name'],
                    'str_Last_Name':     data['str_Last_Name'],
                    'str_Full_Name':     f"{data['str_First_Name']} {data['str_Last_Name']}",
                    'str_Location':      data['str_Location'],
                    'str_Email':         data['str_Email'],
                    'str_Password_hash': encrypted,
                    'dte_Created_Date':  datetime.utcnow(),
                    'lng_Created_By':    data['User_ID'],
                    'bln_IsActive':      True,
                    'bln_IsDeleted':     False
                }
                conn.execute(insert(tbl_User).values(user_rec))
                conn.commit()

            return {'ErrorCode': 9999, 'Message': 'User saved successfully'}

        except SQLAlchemyError:
            logging.exception('save_user_service')
            return {'ErrorCode': 9998, 'Message': 'Database error'}
        except Exception:
            logging.exception('save_user_service')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}


    @staticmethod
    def get_user_details(user_id: int) -> dict:
        try:
            with engine.connect() as conn:
                stmt = (
                    select(
                        tbl_User.c.lng_User_ID,
                        tbl_User.c.str_First_Name,
                        tbl_User.c.str_Last_Name,
                        tbl_User.c.str_Email,
                        tbl_User.c.str_Full_Name,
                        tbl_User.c.str_Location,
                        tbl_User.c.dte_Created_Date,
                        tbl_User.c.bln_IsActive
                    )
                    .where(
                        tbl_User.c.lng_User_ID == user_id,
                        tbl_User.c.bln_IsDeleted == False
                    )
                )
                row = conn.execute(stmt).fetchone()

            if not row:
                return {'ErrorCode': 9995, 'Message': 'User not found'}

            return {'ErrorCode': 9999, 'User Details': dict(row._mapping)}

        except SQLAlchemyError:
            logging.exception('get_user_details')
            return {'ErrorCode': 9998, 'Message': 'Database error'}
        except Exception:
            logging.exception('get_user_details')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}


    @staticmethod
    def list_users_service() -> dict:
        try:
            with engine.connect() as conn:
                stmt = (
                    select(
                        tbl_User.c.lng_User_ID,
                        tbl_User.c.str_First_Name,
                        tbl_User.c.str_Last_Name,
                        tbl_User.c.str_Email,
                        tbl_User.c.str_Location
                    )
                    .where(tbl_User.c.bln_IsDeleted == False)
                )
                rows = conn.execute(stmt).fetchall()

            users = [dict(r._mapping) for r in rows]
            return {'ErrorCode': 9999, 'Users': users}

        except SQLAlchemyError:
            logging.exception('list_users_service')
            return {'ErrorCode': 9998, 'Message': 'Database error'}
        except Exception:
            logging.exception('list_users_service')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}


    @staticmethod
    def update_user_service(data: dict) -> dict:
        try:
            # 1) Validate IDs
            if 'User_ID' not in data or 'lng_User_ID' not in data:
                return {'ErrorCode': 9997, 'Message': 'Missing User_ID or target ID'}

            with engine.connect() as conn:
                existing = conn.execute(
                    select(tbl_User).where(tbl_User.c.lng_User_ID == data['lng_User_ID'])
                ).fetchone()

                if not existing or existing.bln_IsDeleted:
                    return {'ErrorCode': 9996, 'Message': 'User not found'}

                updates, errors = {}, {}

                # First/Last name
                if data.get('str_First_Name') and data['str_First_Name'] != existing.str_First_Name:
                    updates['str_First_Name'] = data['str_First_Name']
                if data.get('str_Last_Name') and data['str_Last_Name'] != existing.str_Last_Name:
                    updates['str_Last_Name'] = data['str_Last_Name']
                if 'str_First_Name' in updates or 'str_Last_Name' in updates:
                    updates['str_Full_Name'] = (
                        f"{updates.get('str_First_Name', existing.str_First_Name)} "
                        f"{updates.get('str_Last_Name', existing.str_Last_Name)}"
                    )

                # Location
                if data.get('str_Location') and data['str_Location'] != existing.str_Location:
                    updates['str_Location'] = data['str_Location']

                # Email
                if data.get('str_Email') and data['str_Email'] != existing.str_Email:
                    if not validate_email_domain(data['str_Email']):
                        errors['str_Email'] = 'Invalid or unreachable domain'
                    elif check_unique_value(tbl_User, 'str_Email', data['str_Email'], conn):
                        return {'ErrorCode': 9997, 'Message': 'Email already exists'}
                    else:
                        updates['str_Email'] = data['str_Email']

                # Password
                if data.get('str_Password'):
                    valid, msg = validate_password(data['str_Password'])
                    if not valid:
                        errors['str_Password'] = msg
                    else:
                        encrypted = encrypt_password(data['str_Password'])
                        if encrypted and encrypted != existing.str_Password_hash:
                            updates['str_Password_hash'] = encrypted

                if errors:
                    return {'ErrorCode': 9991, 'Message': f'Invalid fields: {errors}'}
                if not updates:
                    return {'ErrorCode': 9998, 'Message': 'No changes detected'}

                updates.update({
                    'lng_Modified_By':   data['User_ID'],
                    'dte_Modified_Date': datetime.utcnow()
                })

                res = conn.execute(
                    update(tbl_User)
                    .where(tbl_User.c.lng_User_ID == data['lng_User_ID'])
                    .values(**updates)
                )
                conn.commit()

            if res.rowcount == 0:
                return {'ErrorCode': 9996, 'Message': 'User not found or already deleted'}

            return {'ErrorCode': 9999, 'Message': 'User updated successfully'}

        except SQLAlchemyError:
            logging.exception('update_user_service')
            return {'ErrorCode': 9998, 'Message': 'Database error'}
        except Exception:
            logging.exception('update_user_service')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}


    @staticmethod
    def delete_user_service(user_id: int) -> dict:
        try:
            with engine.connect() as conn:
                res = conn.execute(
                    update(tbl_User)
                    .where(
                        tbl_User.c.lng_User_ID == user_id,
                        tbl_User.c.bln_IsDeleted == False
                    )
                    .values(
                        bln_IsDeleted=True,
                        dte_Deleted_Date=datetime.utcnow(),
                        lng_Deleted_By=user_id
                    )
                )
                conn.commit()

            if res.rowcount == 0:
                return {'ErrorCode': 9996, 'Message': 'User not found or already deleted'}

            return {'ErrorCode': 9999, 'Message': 'User deleted successfully'}

        except SQLAlchemyError:
            logging.exception('delete_user_service')
            return {'ErrorCode': 9998, 'Message': 'Database error'}
        except Exception:
            logging.exception('delete_user_service')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}
