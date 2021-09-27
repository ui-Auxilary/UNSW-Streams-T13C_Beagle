from src.data_store import data_store
from src.error import InputError

import re

def generate_user_handle(name_first, name_last, data_source):
    ## get an initial value for handle
    handle_init = (name_first + name_last).lower()

    # if length greater than 20 shorten to 20
    if len(handle_init) > 20:
        handle_init = handle_init[0:20]
    
    ## check if we need to concatenate a number for duplicate
    if handle_init in data_source['user_handles']:
        suffix_num = 0
        while f'{handle_init}{suffix_num}' in data_source['user_handles']:
            suffix_num += 1
        user_handle = f'{handle_init}{suffix_num}'
    else:
        user_handle = handle_init
    
    return user_handle

def auth_login_v1(email, password):
    ## Get the data store
    data_source = data_store.get()

    ## Check if email belongs to user
    if email not in data_source['user_emails']:
        raise InputError('Email entered does not belong to a user')

    ## Get user ID from email in data
    for user_id in data_source['user_data']:
        if data_source['user_data'][user_id]['email_address'] == email:
            break
    
    ## Check if password is correct
    if data_source['user_data'][user_id]['password'] != password:
        raise InputError('Password is not correct')

    return {
        'auth_user_id': user_id,
    }

def auth_register_v1(email, password, name_first, name_last):
    ## get the data store
    data_source = data_store.get()

    ## check whether email valid
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.match(pattern, email):
        raise InputError('Invalid email address')
    
    ## check that email is unique
    if email in data_source['user_emails']:
        raise InputError('Email already taken')
    else:
        data_source['user_emails'].append(email)
    
    ## check whether password valid (password must be >= 6 chars)
    if len(password) < 6:
        raise InputError('Password too short')
    
    ## check whether name_first and name_last between 1 and 50 chars inclusive
    name_first_len = len(name_first)
    name_last_len = len(name_last)
    if name_first_len < 1 or name_first_len > 50:
        raise InputError('First name not valid size')
    elif name_last_len < 1 or name_last_len > 50:
        raise InputError('Last name not valid size')

    ## get a unique user_handle
    user_handle = generate_user_handle(name_first, name_last, data_source)
    ## append to database
    data_source['user_handles'].append(user_handle)

    ## get new auth_user_id (length prev + 1)
    new_user_id = len(data_source['user_data'].keys()) + 1
    data_source['user_ids'].append(new_user_id)

    data_source['user_data'][new_user_id] = { 'first_name'   : name_first,
                                              'last_name'    : name_last,
                                              'email_address': email,
                                              'password'     : password,
                                              'user_handle'  : user_handle,
                                            }
    if new_user_id == 1:
        data_source['user_data'][new_user_id]['global_owner'] = True
    else:
        data_source['user_data'][new_user_id]['global_owner'] = False

    return {
        'auth_user_id': new_user_id,
    }

