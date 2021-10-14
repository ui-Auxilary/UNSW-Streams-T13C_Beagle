'''
Contains all functions to access the data_store. No other functions outside
this module should access the data_store directly.

Functions:
    add_user(user_id: int, user_details: tuple,
             password: str, user_handle: str, is_owner: bool)
    get_user(user_id: int) -> dict
    get_user_handles() -> list
    get_user_emails() -> list
    get_user_ids() -> list
    add_member_to_channel(channel_id: int, user_id: int)
    add_channel(channel_id: int, channel_name: str, user_id: int,
                is_public: bool)
    get_channel(channel_id: int) -> dict
    get_channel_ids() -> list
    get_dm_ids() -> list
    add_message(user_id: int, channel_id: int, message_id: int,
                content: str, time_created: int)
    get_message_by_id(message_id: int) -> dict
    get_messages_by_channel(channel_id: int) -> list
    add_session_token(token: str, user_id: int)
    get_user_from_token(token: str) -> int
    edit_user(user_id: int, key: str, new_value: str) 
'''

from src.data_store import data_store

def reset_data_store_to_default():
    '''
    Clears the contents of data_store

    Return Value:
        None
    '''

    ## reset values in data_store
    store = data_store.get()
    store = {
        'user_data'   : {},
        'user_handles': [],
        'user_emails' : [],
        'user_ids'    : [],
        'channel_data': {},
        'channel_ids' : [],
        'message_data': {},
        'token'       : {}
    }

    ## update data_store
    data_store.set(store)

def add_user(user_id, user_details, password, user_handle, is_owner):
    '''
    Adds user to the database

    Arguments:
        user_id        (int): id of user being added
        user_details (tuple):
                name_first (str): first name of user
                name_last  (str):last name of user
                email      (str): email of user
        password       (str): password of user
        user_handle    (str): the generated handle of the user
        is_owner       (bool): whether the user is an owner

    Return Value:
        None
    '''

    # get user's name and email
    name_first, name_last, email = user_details

    # get the data store
    data_source = data_store.get()

    # append user_handle to user_handle list
    data_source['user_handles'].append(user_handle)
    data_source['user_emails'].append(email)
    data_source['user_ids'].append(user_id)

    # add the user data to the database
    data_source['user_data'][user_id] = {
        'first_name'   : name_first,
        'last_name'    : name_last,
        'email_address': email,
        'password'     : password,
        'user_handle'  : user_handle,
        'global_owner' : is_owner,
    }

def get_user(user_id):
    '''
    gets the user data from the database

    Arguments:
        user_id (int): id of user

    Return Value:
        { first_name    (str): user's first name
          last_name     (str): user's last name
          email_address (str): user's email address
          password      (str): user's password
          user_handle   (str): unique alphanumeric handle for user
          global_owner (bool): True if user is global owner else False }
    '''

    data_source = data_store.get()
    return data_source['user_data'][user_id]

def edit_user(user_id, key, new_value):
    # get the data store
    data_source = data_store.get()

    # get old value of property
    old_value = data_source['user_data'][user_id][key]

    if key == 'user_handle':
        data_source['user_handles'].remove(old_value)
        data_source['user_handles'].append(new_value)
    elif key == 'email_address':
        data_source['user_emails'].remove(old_value)
        data_source['user_emails'].append(new_value)

    # edit the property
    data_source['user_data'][user_id][key] = new_value


def get_user_handles():
    '''
    Gets the handles of all users from the database

    Return Value:
        user_handles (list): list of all users' handles
    '''

    data_source = data_store.get()
    return data_source['user_handles']

def get_user_emails():
    '''
    gets the emails of all users from the database

    Arguments:
        None

    Return Value:
        user_emails (list): list of all users' emails
    '''

    data_source = data_store.get()
    return data_source['user_emails']

def get_user_ids():
    '''
    Gets the id's of all users from the database

    Return Value:
        user_ids (list): list of all users' user_ids
    '''

    data_source = data_store.get()
    return data_source['user_ids']

def add_member_to_channel(channel_id, user_id):
    '''
    Adds a user to a channel as a member

    Arguments:
        channel_id (int): id of channel that user is being added to
        user_id    (int): id of user being added to channel

    Return Value:
        None
    '''

    data_source = data_store.get()
    data_source['channel_data'][channel_id]['members'].append(user_id)

def add_channel(channel_id, channel_name, user_id, is_public):
    '''
    adds channel data to the database

    Arguments:
        channel_id   (int): id of channel being added to database
        channel_name (str): name of channel being added to database
        user_id      (int): the user id of the owner of the channel
        is_public    (bool): privacy status of the channel

    Return Value:
        None
    '''

    data_source = data_store.get()

    # create channel and add channel data
    data_source['channel_data'][channel_id] = {
        'name'       : channel_name,
        'owner'      : [user_id],
        'is_public'  : is_public,
        'members'    : [user_id],
        'message_ids': []
    }

    # add channel to channel_ids list
    data_source['channel_ids'].append(channel_id)

def get_channel(channel_id):
    '''
    Gets the channel data from the database from a specific channel_id

    Arguments:
        channel_id (int): id of channel that the data is being retrieved for

    Return Value:
        { name         (str): name of the channel
          owner       (list): list of all channel owners
          is_public   (bool): True if channel public else False
          members     (list): list of members' user_ids
          message_ids (list): list of message_ids for all messages sent}
    '''

    data_source = data_store.get()
    return data_source['channel_data'][channel_id]

def get_channel_ids():
    '''
    Gets a list of all the channel ids from the database

    Arguments:
        None

    Return Value:
        channel_ids (list): list of all channel_ids
    '''

    data_source = data_store.get()
    return data_source['channel_ids']

def get_dm_ids():
    '''
    Gets a list of all the dm ids from the database

    Arguments:
        None

    Return Value:
        dm_ids (list): list of all dm_ids
    '''

    data_source = data_store.get()
    return data_source['dm_ids']

def add_message(user_id, channel_id, message_id, content, time_created):
    '''
    Adds a message to the database from a user

    Arguments:
        user_id      (int): id of user that created the message
        channel_id   (int): id of channel that message was created
        message_id   (int): id of message being added to the database
        content      (str): contents of the message
        time_created (int): time message was created

    Return Value:
        None
    '''

    data_source = data_store.get()
    data_source['message_data'][message_id] = {}
    data_source['channel_data'][channel_id]['message_ids'].append(message_id)
    data_source['message_data'][message_id]['author'] = user_id
    data_source['message_data'][message_id]['content'] = content
    data_source['message_data'][message_id]['time_created'] = time_created

def get_message_by_id(message_id):
    '''
    Gets a specific message from its id

    Arguments:
        message_id (int): id of message being added to the database

    Return Value:
        { author       (int): user_id of message author
          content      (str): content of the message
          time_created (int): time message was created }
    '''

    data_source = data_store.get()
    return data_source['message_data'][message_id]

def get_messages_by_channel(channel_id):
    '''
    gets all the message ids from a specified channel id

    Arguments:
        channel_id (int): id of channel that message was created

    Return Value:
        message_ids (list): list of all message_ids for messages in specific channel
    '''

    data_source = data_store.get()
    return data_source['channel_data'][channel_id]['message_ids']

def add_session_token(token, user_id):
    '''
    adds a user token to the sessions storage

    Arguments:
        token   (str): the token for the session
        user_id (int): user's user_id

    Return Value:
        None
    '''

    data_source = data_store.get()
    data_source['token'][token] = user_id

def get_user_from_token(token):
    '''
    retrieves a user_id for a particular token

    Arguments:
        token   (str): the token for the session

    Return Value:
        user_id (int): user's user_id
    '''

    data_source = data_store.get()
    return data_source['token'][token]

def get_all_valid_tokens():
    '''
    retrieves a set of all currently valid tokens

    Return Value:
        tokens (set): tokens for all currently valid sessions
    '''

    data_source = data_store.get()
    return set(data_source['token'].keys())

def add_owner_to_channel(user_id, channel_id):
    '''
    adds given owner to channel

    Arguments:
        user_id     (int): user_id of new owner member
        channel_id  (int): id of the channel being referred to

    Return Value:
        None
    '''

    data_source = data_store.get()
    ## adds a user to the owner list of the channel
    data_source['channel_data'][channel_id]['owner'].append(user_id)


def remove_owner_from_channel(user_id, channel_id):
    '''
    removes given owner from channel

    Arguments:
        user_id     (int): user_id of new owner member
        channel_id  (int): id of the channel being referred to

    Return Value:
        None
    '''

    data_source = data_store.get()
    ## adds a user to the owner list of the channel
    data_source['channel_data'][channel_id]['owner'].remove(user_id)