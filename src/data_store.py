'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
'''
DATA INSIDE:
    - user_data
        key = auth_user_id
        -> dictionary with keys
            - 'first_name'
            - 'last_name'
            - 'email_address'
            - 'password'
            - 'user_handle'
            - 'global_owner'
    - user_handles
        quick access to all handles
    - user_emails
        quick access to all emails
    - user_ids
        quick access to all user ids
    - channel_data
        key = channel_id
        -> dictionary with keys
            - 'name'
            - 'owner'
            - 'is_public'
            - 'members'
    - channel_ids
        quick access to all channel ids
'''
initial_object = {
    'user_data'   : {},
    'user_handles': [],
    'user_emails' : [],
    'user_ids'    : [],
    'channel_data': {},
    'channel_ids' : []
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()

