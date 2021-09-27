from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['user_data'] = {}
    store['user_handles'] = []
    store['user_emails'] = []
    store['user_ids'] = []
    store['channel_data'] = {}
    data_store.set(store)
