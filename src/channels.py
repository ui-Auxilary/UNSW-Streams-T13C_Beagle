from src.data_store import data_store
from src.error import InputError

def channels_list_v1(auth_user_id):
    ## get data
    data_source = data_store.get()

    channel_list = []
    ## get channel id
    for channel in data_source['channel_data']:
        if auth_user_id in data_source['channel_data'][channel]['members']:
            channel_list.append({
                'channel_id': channel,
                'name': data_source['channel_data'][channel]['name']
            })
            
    return {
        'channels': channel_list,
    }

def channels_listall_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_create_v1(auth_user_id, name, is_public):
    ## get data from database
    data_source = data_store.get()

    ## check whether user exists
    user_found = False    
    for user_id in data_source['user_data']:
        if user_id == auth_user_id:
            user_found = True
            break
    if not user_found:
        raise InputError('User ID does not exist')
    
    ## check channel name between 1 and 20 characters
    if not 1 <= len(name) <= 20:
        raise InputError('Invalid channel name size')

    new_channel_id = len(data_source['channel_data'].keys()) + 1
    data_source['channel_data'][new_channel_id] = { 'name'     : name,
                                                    'owner'    : auth_user_id,
                                                    'is_public': is_public,
                                                    'members'  : [auth_user_id] }

    return {
        'channel_id': new_channel_id,
    }
