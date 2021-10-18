'''
Useful helper functions to perform basic repeated operations

Functions:

    clear_v1() -> dict
    check_user_exists(auth_user_id: str)
'''

import jwt

from src.data_operations import (
    get_user_ids,
    reset_data_store_to_default,
    get_user_from_token,
    get_all_valid_tokens,
    add_session_token
)
from src.error import AccessError
from datetime import datetime
from random import randint

def clear_v1():
    '''
    Resets the contents of data_store

    Return Value:
        {}
    '''
    reset_data_store_to_default()
    return {}

def check_user_exists(auth_user_id):
    '''
    Clears the contents of data_store

    Arguments:
        auth_user_id (int): The user's user_id

    Exceptions:
        AccessError: Occurs when:
                        - auth_user_id is not a valid id

    Return Value:
        None
    '''

    if auth_user_id not in get_user_ids():
        raise AccessError(description='Auth_user_id does not exist')

def encode_token(user_id):
    SECRET = "DHRUV_IS_SALTY"

    now = datetime.now()
    time_created = now.strftime("%H%M%S")
    number = time_created
    random_number = randint(0, 723978)
    encoded_token = jwt.encode({'user_id': user_id, 'session_start': number, 'random': random_number},
                               SECRET, algorithm='HS256')

    ## Adds active token to database
    add_session_token(encoded_token, user_id)

    return encoded_token

def decode_token(token):
    SECRET = "DHRUV_IS_SALTY"

    ## check if user is valid
    if token not in get_all_valid_tokens():
        raise AccessError(description='Invalid token')

    user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['user_id']

    return user_id
