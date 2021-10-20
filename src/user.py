'''
Handles operations used to alter a user's properties

Functions:
    user_profile_sethandle(token: str, handle_str: str)
'''
import re
from src.error import InputError
from src.data_operations import (
    get_user_handles,
    edit_user,
    get_user,
    get_complete_user_ids,
    get_user_emails
)
from src.other import check_user_exists

from src.other import decode_token

def user_profile(token, user_id):
    ## check if valid token and decode it
    auth_user_id = decode_token(token)
    check_user_exists(auth_user_id)

    ## check that user_id is valid
    if user_id not in get_complete_user_ids():
        raise InputError(description='Invalid u_id')

    user_info = get_user(user_id)
    return {
        'user': {
            'u_id': user_id,
            'email': user_info['email_address'],
            'name_first': user_info['first_name'],
            'name_last': user_info['last_name'],
            'handle_str': user_info['user_handle']
        }
    }


def user_profile_setname(token, first_name, last_name):
    ## check if valid token and decode it
    user_id = decode_token(token)
    
    check_user_exists(user_id)

    ## check that new handle is valid length and alphanumeric
    if not 1 <= len(first_name) <= 50:
        raise InputError(description='first name must be between 1 and 50 characters')
    elif not 1 <= len(last_name) <= 50:
        raise InputError(description='last name must be between 1 and 50 characters')

    ## if the names are valid change them
    edit_user(user_id, 'first_name', first_name)
    edit_user(user_id, 'last_name', last_name)

def user_profile_setemail(token, email):
    ## check if valid token and decode it
    user_id = decode_token(token)

    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.match(pattern, email):
        raise InputError(description='Invalid email address')

    ## check that new handle is valid length and alphanumeric
    if email in get_user_emails():
        raise InputError(description='Email already taken')

    ## if the email is valid change it
    edit_user(user_id, 'email_address', email)

def user_profile_sethandle(token, handle_str):
    ## check if valid token and decode it
    user_id = decode_token(token)
    check_user_exists(user_id)

    ## check that new handle is valid length and alphanumeric
    if not 3 <= len(handle_str) <= 20:
        raise InputError(description='handle must be between 3 and 20 characters')
    
    if not handle_str.isalnum():
        raise InputError(description='handle must be alphanumeric')

    ## check that handle is not already taken
    if handle_str in get_user_handles():
        raise InputError(description='handle already taken')

    ## if the handle is valid then edit the user's handle
    edit_user(user_id, 'user_handle', handle_str)
