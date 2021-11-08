'''
Controls creation of channels, retrieves user and global channel lists

Functions:
    channels_list_v1(auth_user_id: int) -> dict
    channels_listall_v1(auth_user_id: int) -> dict
    channels_create_v1(auth_user_id: int, name: str, is_public: bool) -> dict
'''

from src.data_operations import get_channel_ids, get_channel, add_channel
from src.other import decode_token
from src.error import InputError
from datetime import timezone, datetime

def channels_list_v1(token):
    '''
    Returns a list of all the channels with their channel id's and channel name that the user
    is a member of

    Arguments:
        auth_user_id (int): id of user

    Exceptions:
        AccessError: Occurs when:
                        - invalid auth_user_id

    Return Value:
        { channels (list): list of all channel dicts a given user is member of }
    '''

    auth_user_id = decode_token(token)

    channel_list = []
    ## get channel id
    for channel in get_channel_ids():
        if auth_user_id in get_channel(channel)['members']:
            channel_list.append({
                'channel_id': channel,
                'name'      : get_channel(channel)['name']
            })

    return {
        'channels': channel_list,
    }

def channels_listall_v1(token):
    '''
    Provides a list of all channels including private channels, and their associated details

    Arguments:
        auth_user_id (int)      - id of user

    Exceptions:
        InputError              - None
        AccessError             - invalid auth_id

    Return Value:
        { channels (list): list of all channel dicts a given user is member of }
    '''

    decode_token(token)

    all_channels = []
    ## get all channel ids
    for channel in get_channel_ids():
        all_channels.append({
            'channel_id': channel,
            'name'      : get_channel(channel)['name']
        })

    return {
        'channels': all_channels,
    }

def channels_create_v1(token, name, is_public):
    '''
    Creates a new channel with a given name that is public or private. The user that
    creates it automatically joins the channel as an owner member

    Arguments:
        auth_user_id (int): id of user that is creating the channel
        name         (str): name of the new channel
        is_public   (bool): the privacy status of the channel

    Exceptions:
        InputError: Occurs when:
                        - user id does not exist
                        - invalid channel name size
        AccessError: invalid auth_id

    Return Value:
        { channel_id (int): unique id that references the created channel }
    '''

    auth_user_id = decode_token(token)

    ## check channel name between 1 and 20 characters
    if not 1 <= len(name) <= 20:
        raise InputError(description='Invalid channel name size')

    ## get a new id for the channel and add channel to system
    new_channel_id = len(get_channel_ids()) + 1
    dt = datetime.now()
    time_created = int(dt.replace(tzinfo=timezone.utc).timestamp())
    add_channel(new_channel_id, name, auth_user_id, is_public, time_created)

    return {
        'channel_id': new_channel_id,
    }
