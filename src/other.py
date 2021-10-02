from src.data_store import data_store
from src.data_operations import get_user_ids
from src.error import AccessError

def clear_v1():
    store = data_store.get()
    store['user_data'] = {}
    store['user_handles'] = []
    store['user_emails'] = []
    store['user_ids'] = []
    store['channel_data'] = {}
    store['channel_ids'] = []
    store['message_data'] = {}
    data_store.set(store)
    return {}

def check_user_exists(auth_user_id):
    # check if auth_user_id is valid
    if auth_user_id not in get_user_ids():
        raise AccessError('Auth_user_id does not exist')
