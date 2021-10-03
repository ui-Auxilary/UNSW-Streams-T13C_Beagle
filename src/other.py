'''
Useful helper functions to perform basic repeated operations

Functions:

    clear_v1() -> dict
    check_user_exists(auth_user_id: str)
'''

from src.data_operations import get_user_ids, reset_data_store_to_default
from src.error import AccessError

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
        raise AccessError('Auth_user_id does not exist')
