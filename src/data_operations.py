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
    add_member_to_channel(channel_id: int, user_id: int, time_updated: int)
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
    remove_dm(dm_id: int)
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
    get_user_notifications(user_id: int) -> list
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
from datetime import timezone, datetime
from typing_extensions import TypedDict
from typing import Dict, Tuple

class get_user_type(TypedDict):
    first_name: str
    last_name: str
    email_address: str
    password: str
    user_handle: str
    global_owner: bool

class get_channel_type(TypedDict):
    name: str
    owner: int
    is_public: bool
    members: list
    message_ids: list
    
class get_dm_type(TypedDict):
    name: str
    owner: int
    members: list
    message_ids: list

class get_message_by_id_type(TypedDict):
    author: int
    content: str
    time_created: int
    
class get_user_stats_type(TypedDict):
    channels_joined: int
    dms_joined: int
    messages_sent: int
    involvement_rate: float
    
class get_workspace_stats_type(TypedDict):
    channels_exist: int
    dms_exist: int
    messages_exist: int
    utilization_rate: float


def reset_data_store_to_default() -> None:
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
        'workspace_stats': {},
        'user_stats': {}
    }

    # update data_store
    data_store.set(store)


def add_user(user_id: int, user_details: tuple, password: str, user_handle: str, is_owner: bool) -> None:
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
        'notifications': [],
        'messages_sent': 0,
        'in_channels': [],
        'in_dms': [],
    }

    if is_owner:
        data_source['global_owners'].append(user_id)


def remove_user_details(user_id: int) -> None:
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


def get_user_channels(user_id: int) -> list:
    '''
    Gets the list of channels the user is currently in

    Arguments:
        user_id (int): id of user

    Return Value:
        user_channels (list): list of all users' channels
    '''

    data_source = data_store.get()

    return data_source['user_data'][user_id]['in_channels']


def get_user_dms(user_id: int) -> list:
    '''
    Gets the list of channels the user is currently in

    Arguments:
        user_id (int): id of user

    Return Value:
        user_channels (list): list of all users' channels
    '''

    data_source = data_store.get()

    return data_source['user_data'][user_id]['in_dms']


def get_user(user_id: int) -> get_user_type:
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


def edit_user(user_id: int, key: str, new_value: str) -> None:
    '''
    Edits the user's handle or email of the user

    Arguments:
        user_id          (int): id of user who's permissions will change
        key              (str): the user's email or handle
        new_value        (str): the user's new email or handle

    Return Value:
        None
    '''
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


def edit_user_permissions(user_id: int, permission_id: int) -> None:
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


def get_user_handles() -> list:
    '''
    Gets the handles of all users from the database

    Arguments:
        None

    Return Value:
        user_handles (list): list of all users' handles
    '''

    data_source = data_store.get()
    return data_source['user_handles']


def get_user_emails() -> list:
    '''
    gets the emails of all users from the database

    Arguments:
        None

    Return Value:
        user_emails (list): list of all users' emails
    '''

    data_source = data_store.get()
    return data_source['user_emails']


def get_user_ids() -> list:
    '''
    Gets the id's of all users from the database

    Arguments:
        None

    Return Value:
        user_ids (list): list of all users' user_ids
    '''

    data_source = data_store.get()
    return data_source['user_ids']


def get_complete_user_ids() -> list:
    '''
    Gets the id's of all users from the database

    Arguments:
        None

    Return Value:
        user_ids (list): list of all users' user_ids
    '''

    data_source = data_store.get()
    return data_source['user_data'].keys()


def add_member_to_channel(channel_id: int, user_id: int, time_updated: int) -> None:
    '''
    Adds a user to a channel as a member

    Arguments:
        channel_id      (int): id of channel that user is being added to
        user_id         (int): id of user being added to channel
        time_updated    (int): time when user is added to channel

    Return Value:
        None
    '''

    data_source = data_store.get()

    data_source['channel_data'][channel_id]['members'].append(user_id)
    data_source['user_data'][user_id]['in_channels'].append(channel_id)

    num_of_channels = len(data_source['user_data'][user_id]['in_channels'])
    channel_data = {
        'num_channels_joined': num_of_channels,
        'time_stamp': time_updated
    }

    update_user_stats(user_id, channel_data, False, False)


def remove_member_from_channel(channel_id: int, user_id: int, time_updated: int) -> None:
    '''
    Removes a user from a channel

    Arguments:
        channel_id      (int): id of channel that user is being removed from
        user_id         (int): id of user being removed from channel
        time_updated    (int): time when member is removed from channel

    Return Value:
        None
    '''
    data_source = data_store.get()

    if user_id in data_source['channel_data'][channel_id]['owner']:
        data_source['channel_data'][channel_id]['owner'].remove(user_id)
    data_source['channel_data'][channel_id]['members'].remove(user_id)
    data_source['user_data'][user_id]['in_channels'].remove(channel_id)

    num_of_channels = len(data_source['user_data'][user_id]['in_channels'])
    channel_data = {
        'num_channels_joined': num_of_channels,
        'time_stamp': time_updated
    }

    update_user_stats(user_id, channel_data, False, False)


def add_channel(channel_id: int, channel_name: str, user_id: int, is_public: bool, time_created: int) -> None:
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
        'message_ids': [],
        'time_created': time_created
    }

    # add channel to channel_ids list and channel to users' list of channels
    data_source['channel_ids'].append(channel_id)
    data_source['user_data'][user_id]['in_channels'].append(channel_id)

    num_user_channels = len(data_source['user_data'][user_id]['in_channels'])
    channel_data = {
        'num_channels_joined': num_user_channels,
        'time_stamp': time_created
    }

    update_user_stats(user_id, channel_data, False, False)

    num_of_channels = len(data_source['channel_ids'])
    channel_data_2 = {
        'num_channels_exist': num_of_channels,
        'time_stamp': time_created
    }

    update_workspace_stats(channel_data_2, False, False)


def get_channel(channel_id: int) -> get_channel_type:
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


def get_channel_messages(channel_id: int) -> list:
    '''
    Gets a list of all the channel messages from the channel

    Arguments:
        channel_id        (int): id of channel

    Return Value:
        channel_messages (list): list of all channel messages
    '''

    data_source = data_store.get()
    return data_source['channel_data'][channel_id]['message_ids']


def get_dm_messages(dm_id: int) -> list:
    '''
    Gets a list of all the dm messages from the dm

    Arguments:
        dm_id        (int): id of dm

    Return Value:
        dm_messages (list): list of all dm messages
    '''

    data_source = data_store.get()
    return data_source['dm_data'][dm_id]['message_ids']


def get_channel_ids() -> list:
    '''
    Gets a list of all the channel ids from the database

    Arguments:
        None

    Return Value:
        channel_ids (list): list of all channel_ids
    '''

    data_source = data_store.get()
    return data_source['channel_ids']


def remove_member_from_dm(dm_id: int, user_id: int, time_updated: int) -> None:
    '''
    Removes a user from a dm

    Arguments:
        dm_id   (int): id of dm that user is being removed from
        user_id     (int): id of user being removed from dm
        time_updated    (int): time when member is removed from dm

    Return Value:
        None
    '''
    data_source = data_store.get()

    if user_id in data_source['dm_data'][dm_id]['owner']:
        data_source['dm_data'][dm_id]['owner'].remove(user_id)
    data_source['dm_data'][dm_id]['members'].remove(user_id)
    data_source['user_data'][user_id]['in_dms'].remove(dm_id)

    num_of_dms = len(data_source['user_data'][user_id]['in_dms'])
    dm_data = {
        'num_channels_joined': num_of_dms,
        'time_stamp': time_updated
    }

    update_user_stats(user_id, False, dm_data, False)


def add_user_to_dm(dm_id: int, user_id: int, time_updated: int) -> None:
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

    num_of_dms = len(data_source['user_data'][user_id]['in_dms'])

    dm_data = {
        'num_dms_joined': num_of_dms,
        'time_stamp': time_updated
    }

    update_user_stats(user_id, False, dm_data, False)


def add_dm(dm_id: int, dm_name: str, auth_user_id: int, time_created: int) -> None:
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
        'members': [auth_user_id],
        'message_ids': [],
        'time_created': time_created
    }

    # add dm to dm_ids list
    data_source['dm_ids'].append(dm_id)
    data_source['dm_data'][dm_id]['owner'].append(auth_user_id)
    data_source['user_data'][auth_user_id]['in_dms'].append(dm_id)

    num_of_dms = len(data_source['dm_ids'])

    dm_data = {
        'num_dms_exist': num_of_dms,
        'time_stamp': time_created
    }

    update_workspace_stats(False, dm_data, False)

    num_of_dms = len(data_source['user_data'][auth_user_id]['in_dms'])

    dm_data = {
        'num_dms_joined': num_of_dms,
        'time_stamp': time_created
    }

    update_user_stats(auth_user_id, False, dm_data, False)


def get_dm(dm_id: int) -> get_dm_type:
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


def get_dm_ids() -> list:
    '''
    Gets a list of all the dm ids from the database

    Arguments:
        None

    Return Value:
        dm_ids (list): list of all dm_ids
    '''

    data_source = data_store.get()
    return data_source['dm_ids']


def remove_dm(dm_id: int, time_updated: int) -> None:
    '''
    Removes a dm, from the database list of DMs

    Arguments:
        dm_id (int): id of dm being removed

    Return Value:
        None
    '''

    data_source = data_store.get()
    data_source['dm_ids'].remove(dm_id)
    num_of_dms = len(data_source['dm_ids'])

    dm_data = {
        'num_dms_exist': num_of_dms,
        'time_stamp': time_updated
    }

    update_workspace_stats(False, dm_data, False)


def get_global_owners() -> list:
    '''
    Gets a list of all the global owners from the database

    Arguments:
        None

    Return Value:
        global_owners (list): list of all global_owners
    '''

    data_source = data_store.get()
    return data_source['global_owners']


def add_message(is_channel: bool, user_id: int, channel_id: int, message_id: int, content: str, time_created: int) -> None:
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
        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
        'is_pinned': False
    }

    # add message to the channel's message list
    if is_channel:
        data_source['channel_data'][channel_id]['message_ids'].append(
            message_id)
    else:
        data_source['dm_data'][channel_id]['message_ids'].append(message_id)

    # add unique message id to message_ids list
    data_source['message_ids'].append(message_id)
    data_source['user_data'][user_id]['messages_sent'] += 1

    num_of_messages = len(data_source['message_ids'])

    message_data = {
        'num_messages_exist': num_of_messages,
        'time_stamp': time_created
    }

    update_workspace_stats(False, False, message_data)

    num_user_messages = data_source['user_data'][user_id]['messages_sent']
    message_data = {
        'num_messages_sent': num_user_messages,
        'time_stamp': time_created
    }

    update_user_stats(user_id, False, False, message_data)


def add_standup_message(channel_id: int, content: str) -> None:
    '''
    Adds a message to the database from a user

    Arguments:
        channel_id   (int): id of channel
        content      (str): contents of the message

    Return Value:
        None
    '''

    data_source = data_store.get()
    data_source['channel_data'][channel_id]['standup_data']['message_package'].append(
        content)


def clear_message_pack(channel_id: int) -> None:
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


def edit_message(is_channel: bool, channel_id: int, message_id: int, message: str) -> None:
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
        dt = datetime.now()
        time_created = int(dt.timestamp())

        remove_message(is_channel, channel_id, message_id, time_created)
    elif message == 'Removed user':
        data_source['message_data'][message_id]['content'] = 'Removed user'
    else:
        data_source['message_data'][message_id]['content'] = message


def remove_message(is_channel: bool, channel_id: int, message_id: int, time_updated: int) -> None:
    '''
    Removes a message from the datastore and associated channels/dms

    Arguments:
        is_channel  (bool): bool of whether the message is from a channel
        channel_id   (int): id of channel
        message_id   (int): id of message being added to the database
        time_updated (int): time when the message is removed

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

    num_of_messages = len(data_source['message_ids'])

    message_data = {
        'num_messages_exist': num_of_messages,
        'time_stamp': time_updated
    }

    update_workspace_stats(False, False, message_data)

    message_data = {
        'num_messages_exist': num_of_messages,
        'time_stamp': time_updated
    }


def get_message_ids() -> list:
    '''
    Gets a list of all the message ids from the database

    Arguments:
        None

    Return Value:
        message_ids (list): list of all message_ids
    '''

    data_source = data_store.get()
    return data_source['message_ids']


def get_message_content(message_id: int) -> Dict[str, str]:
    '''
    Gets a specific message from its id

    Arguments:
        message_id (int): id of message being added to the database

    Return Value:
        {content      (str): content of the message}
    '''
    data_source = data_store.get()
    return data_source['message_data'][message_id]['content']


def get_message_by_id(message_id: int) -> get_message_by_id_type:
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


def get_messages_by_channel(channel_id: int) -> list:
    '''
    gets all the message ids from a specified channel id

    Arguments:
        channel_id (int): id of channel that message was created

    Return Value:
        message_ids (list): list of all message_ids for messages in specific channel
    '''

    data_source = data_store.get()
    return data_source['channel_data'][channel_id]['message_ids']


def get_messages_by_dm(dm_id: int) -> list:
    '''
    gets all the message ids from a specified dm id

    Arguments:
        dm_id       (int): id of channel that message was created

    Return Value:
        message_ids (list): list of all message_ids for messages in specific channel
    '''

    data_source = data_store.get()
    return data_source['dm_data'][dm_id]['message_ids']


def add_notification(is_channel: bool, channel_id: int, user_id: int, content: str) -> None:
    '''
    adds a notifcation to the database

    Arguments:
        is_channel       (bool): whether or not the channel is a channel or dm
        channel_id        (int): id of channel parsed
        user_id           (int): the id of the user retrieving notifications
        content           (str): content of the notification

    Return Value:
        None
    '''

    data_source = data_store.get()

    if is_channel:
        data_source['user_data'][user_id]['notifications'].append({
            'channel_id': channel_id,
            'dm_id': -1,
            'content': content,
        })
    else:
        data_source['user_data'][user_id]['notifications'].append({
            'channel_id': -1,
            'dm_id': channel_id,
            'content': content,
        })


def get_user_notifications(user_id: int) -> list:
    '''
    Gets a list of a user's notifications

    Arguments:
        user_id      (int): id of user we are retrieving notifications for

    Return Value:
        notifications (list): list of all the user's notifications
    '''

    data_source = data_store.get()

    return data_source['user_data'][user_id]['notifications']


def set_active_standup(set_active: bool, channel_id: int, time_finished: int) -> None:
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


def add_user_profileimage(user_id: int, cropped_image) -> None:
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


def add_session_token(token: str, user_id: int) -> None:
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


def remove_session_token(token: str) -> None:
    '''
    removes a user token to the sessions storage

    Arguments:
        token   (str): the token for the session

    Return Value:
        None
    '''

    data_source = data_store.get()
    del data_source['token'][token]


def get_all_valid_tokens() -> set:
    '''
    retrieves a set of all currently valid tokens

    Return Value:
        tokens (set): tokens for all currently valid sessions
    '''

    data_source = data_store.get()
    return set(data_source['token'].keys())


def add_passwordreset_key(user_id: int, reset_key: str) -> None:
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


def get_passwordreset_key(reset_key: str) -> Tuple[bool, str]:
    '''
    gets reset code associated with a user

    Arguments:
        reset_key (str): unique password reset request key

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


def add_owner_to_channel(user_id: int, channel_id: int) -> None:
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


def remove_owner_from_channel(user_id: int, channel_id: int) -> None:
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


# def add_react(user_id, message_id, react_id):
#     '''
#     adds new react to the reacts list

#     Arguments:
#         user_id     (int): user_id of new owner member
#         message_id  (int): id of message being reacted
#         react_id    (int): id of the react

#     Return Value:
#         None
#     '''
#     data_source = data_store.get()
#     data_source['message_data'][message_id]['reacts']['is_this_user_reacted'] = True


def react_message(user_id: int, message_id: int, react_id: int) -> None:
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
    index = len(data_source['message_data'][message_id]['reacts']) - 1
    data_source['message_data'][message_id]['reacts'][index]['react_id'] = react_id

    in_user_id = data_source['message_data'][message_id]['reacts'][index]['u_ids']

    if user_id not in in_user_id:
        data_source['message_data'][message_id]['reacts'][index]['is_this_user_reacted'] = True
        in_user_id.append(user_id)
    else:
        data_source['message_data'][message_id]['reacts'][index]['is_this_user_reacted'] = False
        in_user_id.remove(user_id)


def calculate_utilization_rate(users_in_channels_or_dms: int, total_users: int) -> float:
    '''
    calculates utilization rate

    Arguments:
        users_in_channels_or_dms    (int): number of users who are in atleast one channel or dm
        total_users                 (int): total number of users in the database
    '''
    if users_in_channels_or_dms == 0 or total_users == 0:
        rate = 0.0
    else:
        rate = float(users_in_channels_or_dms / total_users)

    return rate


def initialise_workspace_stats() -> None:
    '''
    adds workspace stats

    Arguments:
        None

    Return Value:
        None
    '''
    dt = datetime.now()
    time_intialised = int(dt.timestamp())

    data_source = data_store.get()
    data_source['workspace_stats']['channels_exist'] = [{
        'num_channels_exist': 0,
        'time_stamp': time_intialised
    }]
    data_source['workspace_stats']['dms_exist'] = [{
        'num_dms_exist': 0,
        'time_stamp': time_intialised
    }]
    data_source['workspace_stats']['messages_exist'] = [{
        'num_messages_exist': 0,
        'time_stamp': time_intialised
    }]
    data_source['workspace_stats']['utilization_rate'] = 0.0


def initialise_user_stats(user_id: int) -> None:
    '''
    initialises a user's stats

    Arguments:
        user_id     (int): id of the user

    Return Value:
        None
    '''
    data_source = data_store.get()

    dt = datetime.now()
    time_intialised = int(dt.timestamp())
    data_source['user_stats'][user_id] = {}
    data_source['user_stats'][user_id]['channels_joined'] = [{
        'num_channels_joined': 0,
        'time_stamp': time_intialised
    }]
    data_source['user_stats'][user_id]['dms_joined'] = [{
        'num_dms_joined': 0,
        'time_stamp': time_intialised
    }]
    data_source['user_stats'][user_id]['messages_sent'] = [{
        'num_messages_sent': 0,
        'time_stamp': time_intialised
    }]
    data_source['user_stats'][user_id]['involvement_rate'] = 0.0


def calculate_involvement_rate(numerator: int, denominator: int) -> float:
    '''
    calculates involvement rate

    Arguments:
        numerator       (int): sum(num_channels_joined, num_dms_joined, num_msgs_sent)
        denominator     (int): sum(num_channels, num_dms, num_msgs)

    Return Value:
        involvement_rate    (float): the rate of the user's involvement in the stream
    '''

    print(numerator, denominator)
    if numerator == 0 or denominator == 0:
        rate = 0.0
    else:
        rate = float(numerator / denominator)
        print(rate)
    if rate > 1.0:
        rate = 1.0
    return rate


def update_user_stats(user_id: int, channel_data: dict, dm_data: dict, message_data: dict) -> None:
    '''
    updates a user's stats

    Arguments:
        user_id         (int): id of the user
        channel_data    (dict): dictionary that contains channel data
        dm_data         (dict): dictionary that contains dm data
        message_data    (dict): dictionary that contains message data

    Return Value:
        None
    '''
    data_source = data_store.get()

    if channel_data:
        data_source['user_stats'][user_id]['channels_joined'].append(
            channel_data)
    if dm_data:
        data_source['user_stats'][user_id]['dms_joined'].append(dm_data)
    if message_data:
        data_source['user_stats'][user_id]['messages_sent'].append(
            message_data)

    num_channels_joined = len(get_user_channels(user_id))
    num_dms_joined = len(get_user_dms(user_id))
    users_messages = []
    for message_ids in get_message_ids():
        if get_message_by_id(message_ids)['author'] == user_id:
            users_messages.append(message_ids)

    num_messages_sent = len(users_messages)

    involvement = num_channels_joined + num_dms_joined + num_messages_sent
    denom = len(get_channel_ids()) + len(get_dm_ids()) + len(get_message_ids())
    rate = calculate_involvement_rate(involvement, denom)

    data_source['user_stats'][user_id]['involvement_rate'] = rate


def update_workspace_stats(channel_data: dict, dm_data: dict, message_data: dict) -> None:
    '''
    updates the workspace stats

    Arguments:        
        channel_data    (dict): dictionary that contains channel data
        dm_data         (dict): dictionary that contains dm data
        message_data    (dict): dictionary that contains message data

    Return Value:
        None
    '''
    data_source = data_store.get()

    if channel_data:
        data_source['workspace_stats']['channels_exist'].append(channel_data)
    if dm_data:
        data_source['workspace_stats']['dms_exist'].append(dm_data)
    if message_data:
        data_source['workspace_stats']['messages_exist'].append(message_data)

    users_in_channel_or_dm = []

    for user in get_user_ids():
        if get_user(user)['in_channels'] or get_user(user)['in_dms']:
            users_in_channel_or_dm.append(user)

    rate = calculate_utilization_rate(
        len(users_in_channel_or_dm), len(get_user_ids()))

    data_source['workspace_stats']['utilization_rate'] = rate


def get_user_stats(user_id: int) -> get_user_stats_type:
    '''
    gets the stats of a user

    Arguments:        
        user_id         (int): id of the user

    Return Value:
        user_stats      (dict): contains the stats of a user
    '''
    data_source = data_store.get()

    return data_source['user_stats'][user_id]


def get_workspace_stats() -> get_workspace_stats_type:
    '''
    gets the stats of the workspace

    Arguments:        
        None

    Return Value:
        workspace_stats      (dict): contains the stats of the workspace
    '''
    data_source = data_store.get()

    return data_source['workspace_stats']


def pin_message(message_id: int) -> None:
    '''
    pins a message
    Arguments:        
        message_id  (int): id of the message

    Return Value:
        None
    '''
    data_source = data_store.get()
    pinned = data_source['message_data'][message_id]['is_pinned']
    if pinned == False:
        data_source['message_data'][message_id]['is_pinned'] = True
    else:
        data_source['message_data'][message_id]['is_pinned'] = False


def add_sendlater_id(message_id: int) -> None:
    '''
    Adds a message to the database from a user

    Arguments:
        message_id   (int): id of message being added to the database

    Return Value:
        None
    '''
    data_source = data_store.get()

    data_source['message_ids'].append(message_id)
    data_source['message_data'][message_id] = {
        'author': '',
        'content': '',
        'time_created': '',
        'message_id': '',
        'channel_created': '',
        'is_channel': '',
        'reacts': [],
        'is_pinned': False
    }


def add_dm_sendlater_id(message_id: int) -> None:
    '''
    Adds a message to the database from a user

    Arguments:
        message_id   (int): id of message being added to the database

    Return Value:
        None
    '''
    data_source = data_store.get()

    data_source['dm_ids'].append(message_id)
    data_source['dm_data'][message_id] = {
        'author': '',
        'content': '',
        'time_created': '',
        'message_id': '',
        'channel_created': '',
        'is_channel': '',
        'reacts': [],
        'is_pinned': False
    }


def data_dump() -> None:
    while True:
        data_source = data_store.get()
        with open('data_store.json', 'w') as data_file:
            json.dump(data_source, data_file)

        time.sleep(1)


def data_restore() -> None:
    data_source = data_store.get()

    try:
        with open('data_store.json') as data_file:
            data_source = json.load(data_file)
    except:
        pass

    # save it back purely   for pylint unused global data_source
    with open('data_store.json', 'w') as data_file:
        json.dump(data_source, data_file)
