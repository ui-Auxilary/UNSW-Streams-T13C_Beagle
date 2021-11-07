'''
Useful helper functions to perform basic repeated operations

Functions:

    clear_v1() -> dict
'''

import jwt
import re

from src.data_operations import (
    reset_data_store_to_default,
    get_all_valid_tokens,
    add_session_token,
    clear_active_threads,
<<<<<<< HEAD
=======
    get_user_handles,
>>>>>>> refactor: Added helper functions for other_py to help notifications get the user
    get_user_ids,
    get_user
)

from src.error import AccessError
from datetime import datetime
from random import randint


def clear_v1():
    '''
    Resets the contents of data_store

    Return Value:
        { }
    '''

    clear_active_threads()
    reset_data_store_to_default()
    return {}

def get_uid_by_email(email):
    '''
    Gets a user's id using their email address

    Arguments:
        email (str): a valid email address for the user

    Return Value:
        user_id (int): the user's user_id
    '''

    for person in get_user_ids():
        if get_user(person)['email_address'] == email:
            user_id = person
    
    return user_id

def encode_token(user_id):
    '''
    Generates a unique user session token for a given user_id

    Arguments:
        user_id (int): The user's user_id

    Return Value:
        token (int): A unique user token for the user's session
    '''

    SECRET = "DHRUV_IS_SALTY"

    now = datetime.now()
    time_created = now.strftime("%H%M%S")
    number = time_created
    random_number = randint(0, 723978)
    encoded_token = jwt.encode({'user_id': user_id, 'session_start': number, 'random': random_number},
                               SECRET, algorithm='HS256')

    # Adds active token to database
    add_session_token(encoded_token, user_id)

    return encoded_token


def decode_token(token):
    '''
    Decodes a user token to give the user_id it is associated with

    Arguments:
        user_id (int): The unique user token for the user's session

    Return Value:
        token (int): The user's user_id
    '''
    SECRET = "DHRUV_IS_SALTY"

    # check if user is valid
    if token not in get_all_valid_tokens():
        raise AccessError(description='Invalid token')

    user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['user_id']

    return user_id

def check_valid_tag(message):
    # search for an @tag and up to 20 chars alphanumeric handle
    pattern = r'@([a-zA-Z0-9]{1,20})([^a-zA-Z0-9]|$)'

    if re.search(pattern, message):
        user_handle = re.search(pattern, message)[1]

        if user_handle in get_user_handles():
            return get_user_from_handle(user_handle)       

    else:
        return False

def get_user_from_handle(user_handle):
    for person in get_user_ids():
        if get_user(person)['user_handle'] == user_handle:
            user_id = person
            break
    
    return user_id