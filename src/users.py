'''
Handles high level program-wide user functionality

Functions:
    users_all(token: str) -> dict
'''

from src.error import InputError
from src.data_operations import (
    get_user_handles,
    edit_user,
    get_user,
    get_user_ids,
    get_dm_ids,
    get_dm,
    get_channel_ids,
    get_channel,
    get_message_ids,
    calculate_utilization_rate,
    get_workspace_timestamp
)
from src.other import decode_token


def users_all(token):
    '''
    Returns a list of all users, including user ids, emails, first name, 
    last name and user handle.

    Arguments:
        token        (str): an encoded token containing a users id

    Exceptions:
        InputError: Occurs when:
                        - auth_id does not refer to a valid user
        AccessError: Occurs when:
                        - invalid auth_id

    Return Value:
        {user             (list): contains dictionary of information of each user
            {u_id          (int): unique u_id for each user
             email         (str): email of user
             name_first    (str): first name of user
             name_last     (str): last name of user
             user_handle   (str): unique alphanumeric handle for user
            }
        }
    '''
    user_id = decode_token(token)

    users = {'users': []}

    for user_id in get_user_ids():
        user_info = get_user(user_id)
        users['users'].append({
            'u_id': user_id,
            'email': user_info['email_address'],
            'name_first': user_info['first_name'],
            'name_last': user_info['last_name'],
            'handle_str': user_info['user_handle'],
            'profile_img_url': user_info['image_url']
        })

    return users

def users_stats_v1(token):
    
    
    user_id = decode_token(token)
    users_in_channel_or_dm = []

    for user in users_all(token):
        dms_list = []

        # Check each dm id from all dm ids in the database
        for dm_id in get_dm_ids():
            # Check if user id is a member of the dm
            if user_id in get_dm(dm_id)['members']:
                dms_list.append({
                    'dm_id': dm_id,
                    'name': get_dm(dm_id)['name']
                })

        channel_list = []
        ## get channel id
        for channel in get_channel_ids():
            if user_id in get_channel(channel)['members']:
                channel_list.append({
                    'channel_id': channel,
                    'name'      : get_channel(channel)['name']
            })
        
        if user in dms_list or channel_list:
            users_in_channel_or_dm.append(user)
    rate = calculate_utilization_rate(len(users_in_channel_or_dm), len(users_all(token)))

    num_channels = len(get_channel_ids())
    num_dms = len(get_dm_ids())
    num_messages = len(get_message_ids())
    workspace_stats = {
        'channel_stats': [{
            'num_channels_exist': num_channels,
            'time_stamp': get_workspace_timestamp(1)
        }],
        'dm_stats': [{
            'num_dms_exist': num_dms,
            'time_stamp': get_workspace_timestamp(2)
        }],
        'message_stats': [{
            'num_messages_exist': num_messages,
            'time_stamp': get_workspace_timestamp(3)
        }],
        'utilization_rate': rate
    }
    return workspace_stats
