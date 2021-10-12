'''
Handles operations used to alter a user's properties

Functions:
    user_profile_sethandle(token: str, handle_str: str)
'''

from src.error import InputError
from src.data_operations import (
    get_user_handles,
    edit_user,
    get_user,
    get_user_ids
)

from src.other import decode_token

def user_profile(token, user_id):
    ## check if valid token and decode it
    decode_token(token)

    ## check that user_id is valid
    if user_id not in get_user_ids():
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


def user_profile_sethandle(token, handle_str):
    ## check if valid token and decode it
    user_id = decode_token(token)

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
