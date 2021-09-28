from src.error import InputError, AccessError
from src.data_operations import get_user_ids, get_channel_ids, get_channel, get_user, add_member_to_channel

def channel_invite_v1(auth_user_id, channel_id, u_id):
    ## checks u_id is valid
    if u_id not in get_user_ids():
        raise InputError('User does not exist')
    ## check whether channel exists
    if channel_id not in get_channel_ids():
        raise InputError('Channel does not exist')
    ## check whether user is already member
    if u_id in get_channel(channel_id)['members']:
        raise InputError('New user is already existing member')
    ## checks auth_user is a member of the channel
    if auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError('User is not authorised to invite new members')
    
    ## adds the new user to the channel
    add_member_to_channel(channel_id, u_id)

    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    # check if auth_user_id is valid
    if auth_user_id not in get_user_ids():
        raise AccessError('Auth_user_id does not exist')
    
    # check if channel_id is valid
    if channel_id not in get_channel_ids():
        raise InputError('Channel_id does not exist')

    # check whether user is in channel
    channel_info = get_channel(channel_id)
    channel_members = channel_info['members']

    if auth_user_id not in channel_members:
        raise AccessError('User is not channel member')
    
    # get the owner's information
    owner_details = get_user(channel_info['owner'])
    owner_dict = {}
    owner_dict['u_id'] = channel_info['owner']
    owner_dict['email'] = owner_details['email_address']
    owner_dict['name_first'] = owner_details['first_name']
    owner_dict['name_last'] = owner_details['last_name']
    owner_dict['handle_str'] = owner_details['user_handle']

    # create list of dictionaries with member info
    member_info = []
    for member in channel_members:
        member_details = get_user(member)
        member_dict = {}
        member_dict['u_id'] = member
        member_dict['email'] = member_details['email_address']
        member_dict['name_first'] = member_details['first_name']
        member_dict['name_last'] = member_details['last_name']
        member_dict['handle_str'] = member_details['user_handle']
        member_info.append(member_dict)

    return_dict = {
        'name': channel_info['name'],
        'owner_members': [owner_dict],
        'all_members': member_info,
        'is_public': channel_info['is_public']
    }

    return return_dict

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
    ## check whether channel exists
    if channel_id not in get_channel_ids():
        raise InputError('Channel does not exist')
    ## check whether user already member
    if auth_user_id in get_channel(channel_id)['members']:
        raise InputError('User is existing member')
    ## check whether user has sufficient permissions to join
    if get_channel(channel_id)['is_public'] == False:
        if get_user(auth_user_id)['global_owner'] == False:
            raise AccessError('User cannot join private channel')
    
    ## add them to channel
    add_member_to_channel(channel_id, auth_user_id)

    return {
    }
