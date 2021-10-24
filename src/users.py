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
from src.other import decode_token, check_user_exists

def users_all(token):
    '''
    Returns a list of all users, including user ids, emails, first name, 
    last name and user handle.

    Arguments:
        token        (str): an encoded token containing a users id

    Exceptions:
        InputError: Occurs when:
                        - auth_id does not refer to a valid user
        AccessError: Occurs when:
                        - invalid auth_id

    Return Value:
        {user             (list): contains dictionary of information of each user
            {u_id          (int): unique u_id for each user
             email         (str): email of user
             name_first    (str): first name of user
             name_last     (str): last name of user
             user_handle   (str): unique alphanumeric handle for user
            }
        }
    '''
    user_id = decode_token(token)
    
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

