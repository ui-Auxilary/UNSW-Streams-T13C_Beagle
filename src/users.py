'''
Handles high level program-wide user functionality

Functions:
    users_all(token: str) -> dict
'''

from src.error import InputError
from src.data_operations import (
    get_user_handles,
    edit_user,
    get_user,
    get_user_ids
)
from src.other import decode_token

def users_all(token):
    decode_token(token)

    users = {'users': []}

    for user_id in get_user_ids():
        user_info = get_user(user_id)
        users['users'].append({
            'u_id': user_id,
            'email': user_info['email_address'],
            'name_first': user_info['first_name'],
            'name_last': user_info['last_name'],
            'handle_str': user_info['user_handle']
        })

    return users

