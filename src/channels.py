from src.data_operations import get_channel_ids, get_channel, get_user_ids, add_channel
from src.other import check_user_exists
from src.error import InputError, AccessError

def channels_list_v1(auth_user_id):
    '''
    returns a list of all the channels with their channel id's and channel name that the user
    is a member of

    Arguments:
        auth_user_id (int)      - id of user
        
    Exceptions:
        InputError              - None
        AccessError             - invalid auth_id

    Return Value:
        channel_list : list
    '''
    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    channel_list = []
    ## get channel id
    for channel in get_channel_ids():
        if auth_user_id in get_channel(channel)['members']:
            channel_list.append({
                'channel_id': channel,
                'name': get_channel(channel)['name']
            })
            
    return {
        'channels': channel_list,
    }

def channels_listall_v1(auth_user_id):
    '''
    Provides a list of all channels including private channels, and their associated details

    Arguments:
        auth_user_id (int)      - id of user

    Exceptions:
        InputError              - None
        AccessError             - invalid auth_id

    Return Value:
        { channel_id        : int,
        name : 
            { name          : str,
            owner         : str, 
            is_public     : bool,
            members       : list,
            message_ids   : list
            }        
        }
    '''
    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    all_channels = []
    ## get all channel ids
    for channel in get_channel_ids():
        all_channels.append({
            'channel_id': channel,
            'name': get_channel(channel)['name']
        })

    return {
        'channels': all_channels,
    }

def channels_create_v1(auth_user_id, name, is_public):
    '''
    creates a new channel with a given name that is public or private. The user that
    creates it automatically joins the channel

    Arguments:
        auth_user_id (int)      - id of user that is creating the channel
        name (str)              - name of the new channel
        is_public (bool)        - the privacy status of the channel

    Exceptions:
        InputError              - Occurs when:
                                    - user id does not exist
                                    - invalid channel name size
        AccessError             - invalid auth_id

    Return Value:
        new_channel_id : int
    '''
    ## checks auth_user_id exists
    check_user_exists(auth_user_id)
    
    ## check channel name between 1 and 20 characters
    if not 1 <= len(name) <= 20:
        raise InputError('Invalid channel name size')

    new_channel_id = len(get_channel_ids()) + 1
    add_channel(new_channel_id, name, auth_user_id, is_public)

    return {
        'channel_id': new_channel_id,
    }
