from src.error import InputError, AccessError
from src.data_operations import (
    edit_message,
    edit_user_permissions,
    get_channel_messages,
    get_message_by_id,
    get_messages_by_dm,
    get_user_dms,
    get_user_ids,
    remove_member_from_channel,
    remove_member_from_dm,
    get_global_owners,
    get_user_channels,
    remove_user_details,
    edit_user
)
from src.other import decode_token, check_user_exists

def admin_user_remove_v1(token, u_id):
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## check auth_user is a global owner
    if auth_user_id not in get_global_owners():
        raise AccessError(description='Not an authorised global owner')

    ## check u_id is valid and not the only global owner
    if u_id not in get_user_ids():
        raise InputError(description='Specified user does not exist')
    if u_id in get_global_owners() and len(get_global_owners()) == 1:
        raise InputError(description='Cannot remove the only global owner')

    ## change user's name to Removed user
    edit_user(u_id, 'first_name', 'Removed')
    edit_user(u_id, 'last_name', 'user')

    ## get a list of all the channels the user is in and change the messages
    channels_list = get_user_channels(u_id)
    dm_list = get_user_dms(u_id)

    ## edit channel messages
    for channel_id in channels_list:
        message_id_list = get_channel_messages(channel_id)
        for message_id in message_id_list:
            message_author = get_message_by_id(message_id)['author']
            if message_author == u_id:
                edit_message(True, channel_id, message_id, 'Removed user')
        remove_member_from_channel(channel_id, u_id)

    ## edit dm messages
    for dm_id in dm_list:
        for message_id in get_messages_by_dm(dm_id):
            message_author = get_message_by_id(message_id)['author']
            if message_author == u_id:
                edit_message(False, dm_id, message_id, 'Removed user')
        remove_member_from_dm(dm_id, u_id)

    ## Remove user so data is reuseable
    remove_user_details(u_id)

    return {}

def admin_userpermission_change_v1(token, u_id, permission_id):
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## check auth_user is a global owner
    if auth_user_id not in get_global_owners():
        raise AccessError(description='Not an authorised global owner')

    ## check u_id is valid and not the only global owner
    if u_id not in get_user_ids():
        raise InputError(description='Specified user does not exist')
    if u_id in get_global_owners() and len(get_global_owners()) == 1 and permission_id == 2:
        raise InputError(description='Cannot demote the only global owner')

    valid_permission = [1,2]

    ## check the specified permission_id is valid
    if permission_id not in valid_permission:
        raise InputError(description='Permission does not exist')

    edit_user_permissions(int(u_id), int(permission_id))

    return {}