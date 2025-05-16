import logging
from datetime import datetime
from sqlalchemy import insert, update, select

from CREATE_DB_CODE.tables_creation import tbl_User, connection
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
            required_fields = ['str_Email', 'str_First_Name', 'str_Last_Name','str_Location', 'str_Password']
            missing_fields = [f for f in required_fields if f not in data or not data[f]]
            if missing_fields:
                return {'ErrorCode': 9997, 'Message': f"All fields required: missing {missing_fields}"}
            fmt_ok = {
                'str_Email': validate_email_domain(data['str_Email']),
                # validate_password returns tuple, so unpack first element
                'str_Password': validate_password(data['str_Password'])[0]
            }
            if check_unique_value(tbl_User, 'str_Email', data['str_Email'], connection):
                return {'ErrorCode': 9997, 'Message': 'Email already exists'}

            invalid = [k for k, ok in fmt_ok.items() if not ok]
            if invalid:
                return {'ErrorCode': 9991, 'Message': f'Invalid fields: {invalid}'}

            encrypted_password = encrypt_password(data['str_Password'])
            if not encrypted_password:
                return {'ErrorCode': 9992, 'Message': 'Password encryption failed'}

            user = {
                'str_First_Name': data['str_First_Name'],
                'str_Last_Name': data['str_Last_Name'],
                'str_Full_Name': f"{data['str_First_Name']} {data['str_Last_Name']}",
                'str_Location': data.get('str_Location', ''),
                'str_Email': data['str_Email'],
                'str_Password_hash': encrypted_password,
                'dte_Created_Date': datetime.utcnow(),
                'lng_Created_By': 1,
                'bln_IsActive': True,
                'bln_IsDeleted': False
            }

            connection.execute(insert(tbl_User).values(user))
            connection.commit()
            return {'ErrorCode': 9999, 'Message': 'User saved successfully'}

        except Exception:
            connection.rollback()
            logging.exception('save_user_service')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}

    @staticmethod
    def get_user_details(user_id: int) -> dict:
        try:
            stmt = select(
                tbl_User.c.lng_User_ID,
                tbl_User.c.str_First_Name,
                tbl_User.c.str_Last_Name,
                tbl_User.c.str_Email,
                tbl_User.c.str_Full_Name,
                tbl_User.c.str_Location,
                tbl_User.c.dte_Created_Date,
                tbl_User.c.bln_IsActive
            ).where(
                tbl_User.c.lng_User_ID == user_id,
                tbl_User.c.bln_IsDeleted == False
            )
            row = connection.execute(stmt).fetchone()
            if not row:
                return {'ErrorCode': 9995, 'Message': 'User not found'}
            return {
                'ErrorCode': 9999,
                'User Details': dict(row._mapping)
            }

        except Exception:
            logging.exception('get_user_details')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}

    @staticmethod
    def list_users_service() -> dict:
        try:
            stmt = select(
                tbl_User.c.lng_User_ID,
                tbl_User.c.str_First_Name,
                tbl_User.c.str_Last_Name,
                tbl_User.c.str_Email,
                tbl_User.c.str_Location
            ).where(tbl_User.c.bln_IsDeleted == False)

            rows = connection.execute(stmt).fetchall()
            return {'ErrorCode': 9999, 'Users': [dict(r._mapping) for r in rows]}

        except Exception:
            logging.exception('list_users_service')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}

    @staticmethod
    def update_user_service(data: dict) -> dict:
        try:
            # Check required keys
            if 'User_ID' not in data or 'lng_User_ID' not in data:
                return {'ErrorCode': 9997, 'Message': 'Missing User_ID or target ID'}

            # Fetch existing user
            existing = connection.execute(
                select(tbl_User).where(tbl_User.c.lng_User_ID == data['lng_User_ID'])
            ).fetchone()

            if not existing or existing.bln_IsDeleted:
                return {'ErrorCode': 9996, 'Message': 'User not found'}

            updates = {}
            errors = {}

            # Compare and update first name
            if 'str_First_Name' in data and data['str_First_Name'] != existing.str_First_Name:
                updates['str_First_Name'] = data['str_First_Name']

            # Compare and update last name
            if 'str_Last_Name' in data and data['str_Last_Name'] != existing.str_Last_Name:
                updates['str_Last_Name'] = data['str_Last_Name']

            # If either name is updated, also update full name
            if 'str_First_Name' in updates or 'str_Last_Name' in updates:
                updates['str_Full_Name'] = (
                    f"{updates.get('str_First_Name', existing.str_First_Name)} "
                    f"{updates.get('str_Last_Name', existing.str_Last_Name)}"
                )

            # Compare and update location
            if 'str_Location' in data and data['str_Location'] != existing.str_Location:
                updates['str_Location'] = data['str_Location']

            # Compare and update email
            if 'str_Email' in data and data['str_Email'] != existing.str_Email:
                if not validate_email_domain(data['str_Email']):
                    errors['str_Email'] = "Invalid or unreachable email domain"
                elif check_unique_value(tbl_User, 'str_Email', data['str_Email'], connection):
                    return {'ErrorCode': 9997, 'Message': 'Email already exists'}
                else:
                    updates['str_Email'] = data['str_Email']

            # Compare and update password (encrypt before saving)
            if 'str_Password' in data:
                valid, msg = validate_password(data['str_Password'])
                if not valid:
                    errors['str_Password'] = msg
                else:
                    encrypted = encrypt_password(data['str_Password'])
                    if encrypted != existing.str_Password_hash:
                        updates['str_Password_hash'] = encrypted

            # If there are any validation errors
            if errors:
                return {'ErrorCode': 9991, 'Message': f"Invalid fields: {errors}"}

            # If nothing changed
            if not updates:
                return {'ErrorCode': 9998, 'Message': 'No changes detected'}

            # Add audit fields
            updates['lng_Modified_By'] = data['User_ID']
            updates['dte_Modified_Date'] = datetime.utcnow()

            # Execute update
            result = connection.execute(
                update(tbl_User)
                .where(tbl_User.c.lng_User_ID == data['lng_User_ID'])
                .values(**updates)
            )
            connection.commit()

            if result.rowcount == 0:
                return {'ErrorCode': 9996, 'Message': 'User not found or already deleted'}

            return {'ErrorCode': 9999, 'Message': 'User updated successfully'}

        except Exception:
            connection.rollback()
            logging.exception('update_user_service')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}

    @staticmethod
    def delete_user_service(user_id: int) -> dict:
        try:
            result = connection.execute(
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
            connection.commit()
            if result.rowcount == 0:
                return {'ErrorCode': 9996, 'Message': 'User not found or already deleted'}

            return {'ErrorCode': 9999, 'Message': 'User deleted successfully'}

        except Exception:
            connection.rollback()
            logging.exception('delete_user_service')
            return {'ErrorCode': 9998, 'Message': 'Internal error'}
