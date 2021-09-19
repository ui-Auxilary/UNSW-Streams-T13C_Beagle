from src.data_store import data_store
from src.error import InputError, AccessError

def channel_invite_v1(auth_user_id, channel_id, u_id):
    ## get database
    data_source = data_store.get()

    ## checks u_id is valid
    if u_id not in data_source['user_data']:
        raise InputError('User does not exist')
    ## check whether channel exists
    if channel_id not in data_source['channel_data']:
        raise InputError('Channel does not exist')
    ## check whether user is already member
    if u_id in data_source['channel_data'][channel_id]['members']:
        raise InputError('New user is already existing member')
    ## checks auth_user is a member of the channel
    if auth_user_id not in data_source['channel_data'][channel_id]['members']:
        raise AccessError('User is not authorised to invite new members')
    
    ## adds the new user to the channel
    data_source['channel_data'][channel_id]['members'].append(u_id)

    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    ## get database
    data_source = data_store.get()

    ## check whether channel exists
    if channel_id not in data_source['channel_data']:
        raise InputError('Channel does not exist')
    ## check whether user already member
    if auth_user_id in data_source['channel_data'][channel_id]['members']:
        raise InputError('User is existing member')
    ## check whether user has sufficient permissions to join
    if data_source['channel_data'][channel_id]['is_public'] == False:
        if data_source['user_data'][auth_user_id]['global_owner'] == False:
            raise AccessError('User cannot join private channel')
    
    ## add them to channel
    data_source['channel_data'][channel_id]['members'].append(auth_user_id)
    

    return {
    }
