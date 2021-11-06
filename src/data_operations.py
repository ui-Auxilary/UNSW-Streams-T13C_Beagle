'''
Contains all functions to access the data_store. No other functions outside
this module should access the data_store directly.

Functions:
    add_user(user_id: int, user_details: tuple,
             password: str, user_handle: str, is_owner: bool)
    remove_user_details(user_id: int)
    get_user(user_id: int) -> dict
    edit_user(user_id: int, key: str, new_value: str)
    edit_user_permissions(user_id: int, permission_id: int)
    get_user_handles() -> list
    get_user_emails() -> list
    get_user_ids() -> list
    add_member_to_channel(channel_id: int, user_id: int)
    remove_member_from_channel(channel_id: int, user_id: int)
    add_channel(channel_id: int, channel_name: str, user_id: int,
                is_public: bool)
    get_channel(channel_id: int) -> dict
    get_channel_messages() -> list
    get_channel_ids() -> list
    remove_member_from_dm(dm_id: int, user_id: int)
    get_dm_messages(dm_id: int) -> list
    get_dm(dm_id: int) -> dict
    get_dm_ids() -> list
    dm_remove(dm_id: int)
    get_global_owners() -> list
    add_message(user_id: int, channel_id: int, message_id: int,
                content: str, time_created: int)
    add_standup_message(channel_id: int, content: str)
    clear_message_pack(channel_id: int)
    clear_active_threads()
    edit_message(is_channel: bool, channel_id: int, message_id: int, message: str):
    remove_message(is_channel: bool, channel_id: int, message_id: int, message: str):
    get_message_by_id(message_id: int) -> dict
    get_messages_by_channel(channel_id: int) -> list
    add_react(user_id: int, message_id: int, react_id: int)
    react_message(user_id: int, message_id: int, react_id: int)
    set_active_standup(channel_id: int)
    add_user_profileimage(user_id: int, cropped_image: img)
    add_session_token(token: str, user_id: int)
    remove_session_token(token: str)
    get_user_from_token(token: str) -> int
'''

from src.data_store import data_store
from src import config
import os
import json
import time
import threading


def reset_data_store_to_default():
    '''
    Clears the contents of data_store

    Return Value:
        None
    '''

    # reset values in data_store
    store = data_store.get()

    store = {
        'user_data': {},
        'user_handles': [],
        'user_emails': [],
        'user_ids': [],
        'channel_data': {},
        'channel_ids': [],
        'dm_data': {},
        'dm_ids': [],
        'global_owners': [],
        'message_data': {},
        'message_ids': [],
        'token': {},
        'password_reset_key': {},
    }

    # update data_store
    data_store.set(store)


def add_user(user_id, user_details, password, user_handle, is_owner):
    '''
    Adds user to the database

    Arguments:
        user_id        (int): id of user being added
        user_details   (tuple):
        name_first     (str): first name of user
        name_last      (str):last name of user
        email          (str): email of user
        password       (str): password of user
        user_handle    (str): the generated handle of the user
        is_owner       (bool): whether the user is an owner
        in_channels    (list): list of channels user is in

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
        'first_name': name_first,
        'last_name': name_last,
        'email_address': email,
        'password': password,
        'user_handle': user_handle,
        'global_owner': is_owner,
        'image_url': '',
        'in_channels': [],
        'in_dms': [],
    }

    if is_owner:
        data_source['global_owners'].append(user_id)


def remove_user_details(user_id):
    '''
    Removes the specified user

    Arguments:
        user_id (int): id of user

    Return Value:
        None
    '''

    data_source = data_store.get()

    # get user_handle and email
    user_handle = data_source['user_data'][user_id]['user_handle']
    user_email = data_source['user_data'][user_id]['email_address']

    # set user_handle and email to blank
    data_source['user_data'][user_id]['user_handle'] = ''
    data_source['user_data'][user_id]['email_address'] = ''

    # remove them from the list of emails and user_handles
    data_source['user_handles'].remove(user_handle)
    data_source['user_emails'].remove(user_email)

    data_source['user_ids'].remove(user_id)


def get_user_channels(user_id):
    '''
    Gets the list of channels the user is currently in

    Arguments:
        user_id (int): id of user

    Return Value:
        user_channels (list): list of all users' channels
    '''

    data_source = data_store.get()

    return data_source['user_data'][user_id]['in_channels']


def get_user_dms(user_id):
    '''
    Gets the list of channels the user is currently in

    Arguments:
        user_id (int): id of user

    Return Value:
        user_channels (list): list of all users' channels
    '''

    data_source = data_store.get()

    return data_source['user_data'][user_id]['in_dms']


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


def edit_user_permissions(user_id, permission_id):
    '''
    Edits the user permissions of the user_id

    Arguments:
        user_id          (int): id of user who's permissions will change
        permission_id    (int): permission to give to user

    Return Value:
        None
    '''

    data_source = data_store.get()

    if permission_id == 1:
        data_source['user_data'][user_id]['global_owner'] = True
        data_source['global_owners'].append(user_id)
    if permission_id == 2:
        data_source['user_data'][user_id]['global_owner'] = False
        if user_id in data_source['global_owners']:
            data_source['global_owners'].remove(user_id)


def get_user_handles():
    '''
    Gets the handles of all users from the database

    Arguments:
        None

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

    Arguments:
        None

    Return Value:
        user_ids (list): list of all users' user_ids
    '''

    data_source = data_store.get()
    return data_source['user_ids']


def get_complete_user_ids():
    '''
    Gets the id's of all users from the database

    Arguments:
        None

    Return Value:
        user_ids (list): list of all users' user_ids
    '''

    data_source = data_store.get()
    return data_source['user_data'].keys()


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
    data_source['user_data'][user_id]['in_channels'].append(channel_id)


def remove_member_from_channel(channel_id, user_id):
    '''
    Removes a user from a channel

    Arguments:
        channel_id (int): id of channel that user is being removed from
        user_id    (int): id of user being removed from channel

    Return Value:
        None
    '''
    data_source = data_store.get()

    if user_id in data_source['channel_data'][channel_id]['owner']:
        data_source['channel_data'][channel_id]['owner'].remove(user_id)
    data_source['channel_data'][channel_id]['members'].remove(user_id)
    data_source['user_data'][user_id]['in_channels'].remove(channel_id)


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
        'name': channel_name,
        'owner': [user_id],
        'is_public': is_public,
        'members': [user_id],
        'standup_data': {
            'is_active': False,
            'time_finish': None,
            'message_package': []
        },
        'message_ids': []
    }

    # add channel to channel_ids list and channel to users' list of channels
    data_source['channel_ids'].append(channel_id)
    data_source['user_data'][user_id]['in_channels'].append(channel_id)


def get_channel(channel_id):
    '''
    Gets the channel data from the database from a specific channel_id

    Arguments:
        channel_id (int): id of channel that the data is being retrieved for

    Return Value:
        { name         (str): name of the channel
          owner        (int): int of the owner
          is_public   (bool): True if channel public else False
          members     (list): list of members' user_ids
          message_ids (list): list of message_ids for all messages sent}
    '''

    data_source = data_store.get()
    return data_source['channel_data'][channel_id]


def get_channel_messages(channel_id):
    '''
    Gets a list of all the channel messages from the channel

    Arguments:
        channel_id        (int): id of channel

    Return Value:
        channel_messages (list): list of all channel messages
    '''

    data_source = data_store.get()
    return data_source['channel_data'][channel_id]['message_ids']

def get_dm_messages(dm_id):
    '''
    Gets a list of all the dm messages from the dm

    Arguments:
        dm_id        (int): id of dm

    Return Value:
        dm_messages (list): list of all dm messages
    '''

    data_source = data_store.get()
    return data_source['dm_data'][dm_id]['message_ids']


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


def remove_member_from_dm(dm_id, user_id):
    '''
    Removes a user from a dm

    Arguments:
        dm_id (int): id of dm that user is being removed from
        user_id    (int): id of user being removed from dm

    Return Value:
        None
    '''
    data_source = data_store.get()

    if user_id in data_source['dm_data'][dm_id]['owner']:
        data_source['dm_data'][dm_id]['owner'].remove(user_id)
    data_source['dm_data'][dm_id]['members'].remove(user_id)
    data_source['user_data'][user_id]['in_dms'].remove(dm_id)


def add_user_to_dm(dm_id, user_id):
    '''
    adds user to a dm

    Arguments:
        dm_id           (int): id of dm being added to database
        user_id         (int): the id of the user being added to the dm

    Return Value:
        None
    '''

    data_source = data_store.get()
    data_source['dm_data'][dm_id]['members'].append(user_id)
    data_source['user_data'][user_id]['in_dms'].append(dm_id)


def add_dm(dm_id, dm_name, auth_user_id):
    '''
    adds dm data to the database

    Arguments:
        dm_id             (int): id of dm being added to database
        dm_name           (str): name of dm being added to database
        auth_user_id      (int): the user id of the owner of the dm

    Return Value:
        None
    '''

    data_source = data_store.get()

    # create dm and add dm data
    data_source['dm_data'][dm_id] = {
        'name': dm_name,
        'owner': [auth_user_id],
        'members': [],
        'message_ids': []
    }

    # add dm to dm_ids list
    data_source['dm_ids'].append(dm_id)
    data_source['dm_data'][dm_id]['owner'].append(auth_user_id)
    data_source['user_data'][auth_user_id]['in_dms'].append(dm_id)


def get_dm(dm_id):
    '''
    Gets the dm data from the database for a specific dm_id

    Arguments:
        dm_id (int): id of dm that the data is being retrieved for

    Return Value:
        { name         (str): name of the dm
          owner        (int): owner
          members     (list): list of members' user infos
          message_ids (list): list of message_ids for all messages sent }
    '''
    data_source = data_store.get()
    return data_source['dm_data'][dm_id]


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


def remove_dm(dm_id):
    '''
    Removes a dm, from the database list of DMs

    Arguments:
        dm_id (int): id of dm being removed

    Return Value:
        None
    '''

    data_source = data_store.get()
    data_source['dm_ids'].remove(dm_id)


def get_global_owners():
    '''
    Gets a list of all the global owners from the database

    Arguments:
        None

    Return Value:
        global_owners (list): list of all global_owners
    '''

    data_source = data_store.get()
    return data_source['global_owners']


def add_message(is_channel, user_id, channel_id, message_id, content, time_created, reacts, is_pinned):
    '''
    Adds a message to the database from a user

    Arguments:
        is_channel  (bool): bool of whether the message is from a channel
        user_id      (int): id of user that created the message
        channel_id   (int): id of channel that message was created
        message_id   (int): id of message being added to the database
        content      (str): contents of the message
        time_created (int): time message was created
        reacts      (list): stores different reacts
        is_pinned   (bool): bool of whethere the message is pinned

    Return Value:
        None
    '''

    data_source = data_store.get()

    # create message and add message data
    data_source['message_data'][message_id] = {
        'author': user_id,
        'content': content,
        'time_created': time_created,
        'message_id': message_id,
        'channel_created': channel_id,
        'is_channel': is_channel,
        'reacts': reacts,
        'is_pinned': is_pinned
    }

    # add message to the channel's message list
    if is_channel:
        data_source['channel_data'][channel_id]['message_ids'].append(
            message_id)
    else:
        data_source['dm_data'][channel_id]['message_ids'].append(message_id)

    # add unique message id to message_ids list
    data_source['message_ids'].append(message_id)


def add_standup_message(channel_id, content):
    '''
    Adds a message to the database from a user

    Arguments:
        is_channel  (bool): bool of whether the message is from a channel
        content      (str): contents of the message

    Return Value:
        None
    '''

    data_source = data_store.get()
    data_source['channel_data'][channel_id]['standup_data']['message_package'].append(
        content)


def clear_message_pack(channel_id):
    '''
    Clears the message pack in a standup in a channel

    Arguments:
        channel_id   (int): id of channel's messagepack being cleared

    Return Value:
        None
    '''

    data_source = data_store.get()

    data_source['channel_data'][channel_id]['standup_data']['message_package'].clear()


def clear_active_threads():
    for thread in threading.enumerate():
        if isinstance(thread, threading.Timer):
            thread.cancel()


def edit_message(is_channel, channel_id, message_id, message):
    '''
    Edits a message in the datastore

    Arguments:
        is_channel  (bool): bool of whether the message is from a channel
        channel_id   (int): id of channel that message was created
        message_id   (int): id of message being added to the database
        message      (str): contents of the message

    Return Value:
        None
    '''

    data_source = data_store.get()

    # check if message is empty and edit the message
    if not message:
        remove_message(is_channel, channel_id, message_id)
    elif message == 'Removed user':
        data_source['message_data'][message_id]['content'] = 'Removed user'
    else:
        data_source['message_data'][message_id]['content'] = message


def remove_message(is_channel, channel_id, message_id):
    '''
    Removes a message from the datastore and associated channels/dms

    Arguments:
        is_channel  (bool): bool of whether the message is from a channel
        message_id   (int): id of message being added to the database

    Return Value:
        None
    '''

    data_source = data_store.get()

    if is_channel:
        data_source['channel_data'][channel_id]['message_ids'].remove(
            message_id)
    else:
        data_source['dm_data'][channel_id]['message_ids'].remove(message_id)

    data_source['message_ids'].remove(message_id)
    del data_source['message_data'][message_id]


def get_message_ids():
    '''
    Gets a list of all the message ids from the database

    Arguments:
        None

    Return Value:
        message_ids (list): list of all message_ids
    '''

    data_source = data_store.get()
    return data_source['message_ids']


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


def get_messages_by_dm(dm_id):
    '''
    gets all the message ids from a specified dm id

    Arguments:
        dm_id       (int): id of channel that message was created

    Return Value:
        message_ids (list): list of all message_ids for messages in specific channel
    '''

    data_source = data_store.get()
    return data_source['dm_data'][dm_id]['message_ids']


def set_active_standup(set_active, channel_id, time_finished):
    '''
    Sets a channel's active_standup value to True

    Arguments:
        set_active      (bool): set the standup to be active or inactive
        channel_id       (int): id of channel that message was created
        time_finished    (int): time that the standup is set to finish

    Return Value:
        None
    '''

    data_source = data_store.get()

    if set_active:
        data_source['channel_data'][channel_id]['standup_data']['is_active'] = True
        data_source['channel_data'][channel_id]['standup_data']['time_finish'] = time_finished
    else:
        data_source['channel_data'][channel_id]['standup_data']['is_active'] = False


def add_user_profileimage(user_id, cropped_image):
    '''
    saves a copy of a cropped image to a user profilephotos folder and saves the url

    Arguments:
        user_id (int): user's user_id
        cropped_image(jpg): cropped image uploaded

    Return Value:
        None
    '''

    data_source = data_store.get()

    file_name = str(user_id) + ".jpg"
    path = os.getcwd() + "/src/static/imgurl/"
    if not os.path.exists(path):
        os.makedirs(path)
    cropped_image.save(path + file_name)

    # add profile_image_url to user
    data_source['user_data'][user_id]['image_url'] = config.url + \
        'static/imgurl/' + file_name


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


def remove_session_token(token):
    '''
    removes a user token to the sessions storage

    Arguments:
        token   (str): the token for the session

    Return Value:
        None
    '''

    data_source = data_store.get()
    del data_source['token'][token]


def get_all_valid_tokens():
    '''
    retrieves a set of all currently valid tokens

    Return Value:
        tokens (set): tokens for all currently valid sessions
    '''

    data_source = data_store.get()
    return set(data_source['token'].keys())

def add_passwordreset_key(user_id, reset_key):
    '''
    adds a unique password reset request key to
    the data store

    Arguments:
        user_id   (int): user_id for account requesting reset
        reset_key (str): unique password reset request key

    Return Value:
        None
    '''

    data_source = data_store.get()
    data_source['password_reset_key'][reset_key] = user_id

def get_passwordreset_key(reset_key):
    '''
    gets reset code associated with a user

    Arguments:
        user_id   (int): user_id for account requesting reset

    Return Value:
        reset_tuple (tuple):
            - reset_code_exists (bool): True if reset code exists else False
            - reset_code_encoded (str): reset code
    '''

    data_source = data_store.get()
    if reset_key in data_source['password_reset_key']:
        return (True, data_source['password_reset_key'][reset_key])
    else:
        return (False, 0)

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
    # adds a user to the owner list of the channel
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
    # removes a user from the owner list of the channel
    data_source['channel_data'][channel_id]['owner'].remove(user_id)

def add_react(user_id, message_id, react_id):
    '''
    adds new react to the reacts list

    Arguments:
        user_id     (int): user_id of new owner member
        message_id  (int): id of message being reacted
        react_id    (int): id of the react

    Return Value:
        None
    '''
    data_source = data_store.get()
    react_data = {'react_id': react_id, 'u_ids':[user_id]}
    data_source['message_data'][message_id]['reacts'].append(react_data)

def react_message(user_id, message_id, react_id):
    '''
    reacts to a message

    Arguments:
        user_id     (int): user_id of new owner member
        message_id  (int): id of message being reacted
        react_id    (int): id of the react

    Return Value:
        None
    '''
    data_source = data_store.get()
    index = len( data_source['message_data'][message_id]['reacts']) - 1
    data_source['message_data'][message_id]['reacts'][index]['react_id'] = react_id

    in_user_id = data_source['message_data'][message_id]['reacts'][index]['u_ids']
    if user_id not in in_user_id:
        in_user_id.append(user_id)
    else:
        in_user_id.remove(user_id)
        if len(in_user_id) == 0:
            in_user_id.remove()

def data_dump():
    while True:
        data_source = data_store.get()
        with open('data_store.json', 'w') as data_file:
            json.dump(data_source, data_file)

        time.sleep(1)


def data_restore():
    data_source = data_store.get()

    try:
        with open('data_store.json') as data_file:
            data_source = json.load(data_file)
    except:
        pass

    # save it back purely for pylint unused global data_source
    with open('data_store.json', 'w') as data_file:
        json.dump(data_source, data_file)
