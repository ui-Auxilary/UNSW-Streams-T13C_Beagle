from src.data_operations import get_channel_ids, get_channel, get_user_ids, add_channel
from src.other import check_user_exists
from src.error import InputError, AccessError

def channels_list_v1(auth_user_id):
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
    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## check whether user exists
    user_found = False    
    for user_id in get_user_ids():
        if user_id == auth_user_id:
            user_found = True
            break
    if not user_found:
        raise InputError('User ID does not exist')
    
    ## check channel name between 1 and 20 characters
    if not 1 <= len(name) <= 20:
        raise InputError('Invalid channel name size')

    new_channel_id = len(get_channel_ids()) + 1
    add_channel(new_channel_id, name, auth_user_id, is_public)

    return {
        'channel_id': new_channel_id,
    }
