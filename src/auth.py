'''
Register and login users

Functions:
    generate_user_handles(name_first: str, name_last: str) -> str
    auth_login_v1(email: str, password: str) -> dict
    auth_register_v1(email: str, password: str, name_first: str, name_last: str) -> dict

'''

import re
import hashlib
from src.error import InputError
from src.data_operations import (
    add_user,
    get_user_emails,
    get_user_ids,
    get_complete_user_ids,
    get_user_handles,
    get_user,
    add_session_token,
    remove_session_token
)
from src.other import encode_token, decode_token

def generate_user_handle(name_first, name_last):
    '''
    Generates a unique str of the user's first name
    and last name concatenated together in lowercase with
    a maximum of 20 characters

    If a handle is already taken, append the smallest number
    (starting from 0) to the end of the handle. The number
    does not contribute to the 20 character limit

    Arguments:
        name_first (str): first name of user
        name_last  (str): last name of user

    Exceptions:
        None

    Return Value:
        user_handle (str): unique alphanumeric handle for user
    '''

    ## get an initial value for handle
    handle_init = (name_first + name_last).lower()

    ## filters out non-alphanumeric characters from handle
    handle_init = ''.join(filter(str.isalnum, handle_init))

    # if length greater than 20 shorten to 20
    if len(handle_init) > 20:
        handle_init = handle_init[0:20]

    ## check if we need to concatenate a number for duplicate
    if handle_init in get_user_handles():
        suffix_num = 0
        while f'{handle_init}{suffix_num}' in get_user_handles():
            suffix_num += 1
        user_handle = f'{handle_init}{suffix_num}'
    else:
        user_handle = handle_init

    return user_handle

def auth_login_v1(email, password):
    '''
    Logs in user given a valid email and password

    Arguments:
        email    (str): email of user
        password (str): password of user

    Exceptions:
        InputError: Occurs when the following do not exist in the database:
                        - email
                        - password

    Return Value:
        { auth_user_id (int): unique user_id for user }
    '''
    
    ## Get user ID from email in data
    for person in get_user_ids():
        if get_user(person)['email_address'] == email:
            user_id = person
            break

    ## Check if email belongs to user
    if email not in get_user_emails():
        raise InputError(description='Email entered does not belong to a user')

    ## Check if password is correct
    if get_user(user_id)['password'] != hashlib.sha256(password.encode()).hexdigest():
        raise InputError(description='Password is not correct')

    ## add token to session
    user_token = encode_token(user_id)
    add_session_token(user_token, user_id)

    return {
        'token'       : user_token,
        'auth_user_id': user_id
    }

def auth_register_v1(email, password, name_first, name_last):
    '''
    Registers user using an email, password, first name and last name.
    Adds the user's data into the database with a user handle and
    returns a user id

    Arguments:
        email      (str): email of user
        password   (str): password of user
        name_first (str): first name of user
        name_last  (str): last name of user

    Exceptions:
        InputError: Occurs when:
                        - An invalid email pattern is used
                        - Email is already used
                        - Password is too short
                        - First name is an invalid size
                        - Last name is an invalid size

    Return Value:
        { auth_user_id (int): unique user_id for user }
    '''
    ## check whether email valid
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.match(pattern, email):
        raise InputError(description='Invalid email address')

    ## check that email is unique
    if email in get_user_emails():
        raise InputError(description='Email already taken')

    ## check whether password valid (password must be >= 6 chars)
    if len(password) < 6:
        raise InputError(description='Password too short')

    ## check whether name_first and name_last between 1 and 50 chars inclusive
    name_first_len = len(name_first)
    name_last_len = len(name_last)
    if name_first_len < 1 or name_first_len > 50:
        raise InputError(description='First name not valid size')
    if name_last_len < 1 or name_last_len > 50:
        raise InputError(description='Last name not valid size')

    ## get a unique user_handle
    user_handle = generate_user_handle(name_first, name_last)

    ## get new auth_user_id (length prev + 1)
    new_user_id = len(get_complete_user_ids()) + 1

    # check whether user is global owner
    user_information = name_first, name_last, email
    user_global_owner = False
    if new_user_id == 1:
        user_global_owner = True

    # get the hash of the password for security
    p_hash = hashlib.sha256(password.encode()).hexdigest()

    # add user to the system
    add_user(new_user_id, user_information, p_hash, user_handle, user_global_owner)

    ## add token to session
    user_token = encode_token(new_user_id)
    add_session_token(user_token, new_user_id)

    return {
        'token'       : user_token,
        'auth_user_id': new_user_id
    }

def auth_logout_v1(token):
    '''
    Given an active token, invalidates the token to log the user out.

    Arguments:
        token   (str): the token for the session

    Return Value:
        {}
    '''
    decode_token(token)

    remove_session_token(token)

    return {}