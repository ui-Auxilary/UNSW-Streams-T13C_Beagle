import re
from src.error import InputError
from src.data_operations import (
    add_user, 
    get_user_emails, 
    get_user_ids, 
    get_user_handles, 
    get_user
)

def generate_user_handle(name_first, name_last):
    '''
    generates a unique str of the user's first name and last name concatenated together in lowercase with a maximum of 20 characters.
    If a handle is already taken, append the smallest number (starting from 0) to the end of the handle. The number does not contribute
    to the 20 character limit.

    Arguments:
        name_first (str)        - first name of user
        name_last (str)         - last name of user
    

    Exceptions:
        InputError              - Occurs when:
                                - non-alphanumeric characters are in either arguments
        AccessError             - None

    Return Value:
        user_handle : str
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
    logs in user given a valid email and password

    Arguments:
        email (str)             - email of user
        password (str)          - password of user
    

    Exceptions:
        InputError              - Occurs when the following do not exist in the database:
                                - email
                                - password
        AccessError             - None

    Return Value:
        { first_name     : str,
          last_name      : str, 
          email_address  : str,
          password       : str,
          user_handle    : str,
          global_owner   : bool
        }
    '''
    ## Check if email belongs to user
    if email not in get_user_emails():
        raise InputError('Email entered does not belong to a user')

    ## Get user ID from email in data
    for user_id in get_user_ids():
        if get_user(user_id)['email_address'] == email:
            break
    
    ## Check if password is correct
    if get_user(user_id)['password'] != password:
        raise InputError('Password is not correct')

    return {
        'auth_user_id': user_id,
    }

def auth_register_v1(email, password, name_first, name_last):
    '''
    Registers user using an email, password, first name and last name. Adds the user's data into the database with a user handle and returns a user id

    Arguments:
        email (str)             - email of user
        password (str)          - password of user
        name_first (str)        - first name of user
        name_last (str)         - last name of user

    Exceptions:
        InputError              - Occurs when:
                                    - An invalid email pattern is used
                                    - Email is already used
                                    - Password is too short
                                    - First name is an invalid size
                                    - Last name is an invalid size
        AccessError             - None

    Return Value:
        { first_name     : str,
        last_name      : str, 
        email_address  : str,
        password       : str,
        user_handle    : str,
        global_owner   : bool
        }
    '''
    ## check whether email valid
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.match(pattern, email):
        raise InputError('Invalid email address')
    
    ## check that email is unique
    if email in get_user_emails():
        raise InputError('Email already taken')
    
    ## check whether password valid (password must be >= 6 chars)
    if len(password) < 6:
        raise InputError('Password too short')
    
    ## check whether name_first and name_last between 1 and 50 chars inclusive
    name_first_len = len(name_first)
    name_last_len = len(name_last)
    if name_first_len < 1 or name_first_len > 50:
        raise InputError('First name not valid size')
    if name_last_len < 1 or name_last_len > 50:
        raise InputError('Last name not valid size')

    ## get a unique user_handle
    user_handle = generate_user_handle(name_first, name_last)

    ## get new auth_user_id (length prev + 1)
    new_user_id = len(get_user_ids()) + 1
    
    if new_user_id == 1:
        add_user(new_user_id, name_first, name_last, email, password, user_handle, True)
    else:
        add_user(new_user_id, name_first, name_last, email, password, user_handle, False)
    
    return {
        'auth_user_id': new_user_id,
    }

