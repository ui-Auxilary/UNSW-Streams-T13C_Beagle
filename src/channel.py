from src.error import InputError, AccessError
from src.other import check_user_exists
from src.data_operations import get_user_ids, get_channel_ids, get_channel, get_user,\
                                add_member_to_channel, get_messages_by_channel

def channel_invite_v1(auth_user_id, channel_id, u_id):
    
## checks auth_user_id exists
    check_user_exists(auth_user_id)
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
    ## checks auth_user_id exists
    check_user_exists(auth_user_id)
    
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
    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## checks for invalid channel_id
    if channel_id not in get_channel_ids():
        raise InputError('Channel_id does not exist')

    ## checks if auth_user_id is a channel member
    channel_info = get_channel(channel_id)
    channel_members = channel_info['members']

    if auth_user_id not in channel_members:
        raise AccessError('User is not channel member')

    ## add_message(auth_user_id, channel_id, message_id, content, time_created)
    result_arr = []
    ## Gets all the messages in the channel sorted from recent to old
    message_id_list = list(reversed(get_messages_by_channel(channel_id)))
    end = start + 50

    ## checks that start does not exceed total messages
    if len(message_id_list) - 1 < start:
        raise InputError('Start number exceeds total messages')

    for message_pos, message_id in enumerate(message_id_list):
        ## if message in given range
        if message_pos >= start and message_pos < end:
            ## Retrieve all information about message_data
            result_dict = {}
            message_info = get_message_by_id(message_id)
            result_dict['message_id'] = message_id
            result_dict['u_id'] = message_info['author']
            result_dict['message'] = message_info['content']
            result_dict['time_created'] = message_info['time_created']
            result_arr.append(result_dict)
        ## if past 50 messages, then exit
        if message_pos == end: 
            break

    ## checks if 50 messages are displayed
    if end > len(message_id_list) - 1: 
        end = -1
    return {
        'messages': result_arr,
        'start': start, 
        'end': end
    }

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
    ## checks auth_user_id exists
    check_user_exists(auth_user_id)
    
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
