from src import user
from src.error import InputError, AccessError
from src.other import check_user_exists, decode_token
from datetime import timezone, datetime

from src.data_operations import (
    add_dm,
    add_message,
    add_user_to_dm,
    get_dm_ids,
    get_dm,
    get_message_by_id,
    get_message_ids,
    get_messages_by_dm,
    get_user,
    get_user_ids
)

def dm_create_v1(token, u_ids):
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)
    
    ## create a list of users and handles
    user_list = []
    user_handle_list = []

    ## add owner as a member of the dm and handle
    user_profile = get_user(auth_user_id)
    user_list.append({
        'u_id': auth_user_id,
        'email': user_profile['email_address'],
        'name_first': user_profile['first_name'],
        'name_last': user_profile['last_name'],
        'handle_str': user_profile['user_handle'],
    })
    user_handle = get_user(auth_user_id)['user_handle']
    user_handle_list.append(user_handle)

    for user_id in u_ids:
        if int(user_id) not in get_user_ids():
            raise InputError(description="Invalid user(s) id")
        if int(user_id) == auth_user_id:
            raise InputError(description="Cannot add creator to DM")
        else:
            user_profile = get_user(int(user_id))
            user_list.append({
                'u_id': int(user_id),
                'email': user_profile['email_address'],
                'name_first': user_profile['first_name'],
                'name_last': user_profile['last_name'],
                'handle_str': user_profile['user_handle'],
            })
            user_handle = get_user(int(user_id))['user_handle']
            user_handle_list.append(user_handle)

    ## generate dm name
    dm_name = ', '.join(sorted(user_handle_list))

    ## get a new id for the dm and add DM to system
    new_dm_id = len(get_dm_ids()) + 1
    add_dm(new_dm_id, dm_name, auth_user_id)

    ## add each user to the DM
    
    for u_id in user_list:
        add_user_to_dm(new_dm_id, u_id)

    return {
        'dm_id': new_dm_id
    }

def dm_list_v1(token):
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    dms_list = []
    
    user_data = get_user(auth_user_id)
    user_profile = {
        'u_id': auth_user_id,
        'email': user_data['email_address'],
        'name_first': user_data['first_name'],
        'name_last': user_data['last_name'],
        'handle_str': user_data['user_handle'],
    }
    ## Check each dm id from all dm ids in the database
    for dm_id in get_dm_ids():
        
        ## Check if user id is a member of the dm
        if user_profile in get_dm(dm_id)['members']:
            dms_list.append({
                'dm_id': dm_id,
                'name': get_dm(dm_id)['name']
            })

    return {
        'dms': dms_list
    }

def dm_remove_v1(token, dm_id):
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)
    
    ## invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")

    ## Get list of owners and members in the dm
    dm_owner = get_dm(dm_id)['owner']
    dm_members = get_dm(dm_id)['members']    

    ## check if user is the owner of the DM
    if auth_user_id not in dm_owner:
        raise AccessError(description="User is not the owner of the DM")    
   
    ## remove users from members in the DM
    for members in dm_members:
        dm_members.remove(members)
    
    ## remove owner from owners in the DM
    dm_owner.remove(auth_user_id)

    return {}

def dm_details_v1(token, dm_id):
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")
    
    ## get list of owners and members in the dm
    dm_members = get_dm(int(dm_id))['members']
    dm_name = get_dm(int(dm_id))['name']    

    ## check if user exists in DM membes
    user_data = get_user(auth_user_id)
    user_profile = {
        'u_id': auth_user_id,
        'email': user_data['email_address'],
        'name_first': user_data['first_name'],
        'name_last': user_data['last_name'],
        'handle_str': user_data['user_handle'],
    }

    if user_profile not in dm_members:
        raise AccessError(description="User is not a member of the DM")    
    
    # create list of dictionaries with member info
    member_info = []
    for member in dm_members:
        member_dict = {
            'u_id'      : member['u_id'],
            'email'     : member['email'],
            'name_first': member['name_first'],
            'name_last' : member['name_last'],
            'handle_str': member['handle_str']
        }
        member_info.append(member_dict)

    return {
        'name': dm_name,
        'members': member_info
    }

def dm_leave_v1(token, dm_id):
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## Invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")

    ## Get list of owners and members in the dm
    dm_owner = get_dm(dm_id)['owner']
    dm_members = get_dm(dm_id)['members']

    ## check if user exists in DM membes
    user_data = get_user(auth_user_id)
    user_profile = {
        'u_id': auth_user_id,
        'email': user_data['email_address'],
        'name_first': user_data['first_name'],
        'name_last': user_data['last_name'],
        'handle_str': user_data['user_handle'],
    }

    if user_profile not in dm_members:
        raise AccessError(description="User is not a member of the DM")

    ## check if user is the owner of the DM
    if user_profile in dm_owner:
        dm_owner.remove(user_profile)

    ## remove user from members in the DM
    dm_members.remove(user_profile)

    return {}

def dm_messages_v1(token, dm_id, start):
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")

    ## check if user exists in DM membes
    user_data = get_user(auth_user_id)
    user_profile = {
        'u_id': auth_user_id,
        'email': user_data['email_address'],
        'name_first': user_data['first_name'],
        'name_last': user_data['last_name'],
        'handle_str': user_data['user_handle'],
    }

    if user_profile not in get_dm(dm_id)['members']:
        raise AccessError(description="User is not a member of the DM") 

    ## Gets all the messages in the channel sorted from recent to old
    message_id_list = list(reversed(get_messages_by_dm(dm_id)))
    end = start + 50

    ## checks that start does not exceed total messages
    if start > len(message_id_list):
        raise InputError('Start number exceeds total messages')

    result_arr = []
    for message_pos, message_id in enumerate(message_id_list):
        ## if message in given range
        if start <= message_pos < end - 1:
            message_info = get_message_by_id(message_id)
            
            is_channel = False
            ## add a message to the database
            add_message(
                is_channel,
                message_info['author'],
                dm_id, 
                message_id,
                message_info['content'],
                message_info['time_created']
            )
            
            result_arr.append({
                'message_id': message_id,
                'u_id': message_info['author'],
                'message': message_info['content'],
                'time_created': message_info['time_created']
            })
        else:
            break
        
    ## checks if 50 messages are displayed
    if end > len(message_id_list) - 1:
        end = -1

    return {
        'messages': result_arr,
        'start'   : start,
        'end'     : end,
    }
    

def message_senddm_v1(token, dm_id, message):
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")

    ## check if user exists in DM membes
    user_data = get_user(auth_user_id)
    user_profile = {
        'u_id': auth_user_id,
        'email': user_data['email_address'],
        'name_first': user_data['first_name'],
        'name_last': user_data['last_name'],
        'handle_str': user_data['user_handle'],
    }

    if user_profile not in get_dm(dm_id)['members']:
        raise AccessError(description="User is not a member of the DM")     
    
    if not 1 <= len(message) <= 1000:
        raise InputError(description="Invalid message length. Upgrade to nitro")

    ## get length of message_ids
    new_message_id = len(get_message_ids()) + 1
    is_channel = False

    ## time created
    dt = datetime(2015, 10, 19)
    time_created = int(dt.replace(tzinfo=timezone.utc).timestamp())

    ## add message to datastore
    add_message(is_channel, auth_user_id, dm_id, new_message_id, message, time_created)

    return {
        'message_id': new_message_id
    }
