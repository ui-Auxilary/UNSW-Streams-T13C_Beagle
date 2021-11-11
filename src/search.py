from src.error import InputError
from src.other import decode_token

from src.data_operations import (
    get_user_channels,
    get_user_dms,
    get_channel_messages,
    get_message_by_id,
    get_messages_by_dm
)

def search_v1(token, query_str):
    auth_user_id = decode_token(token)

    if not 0 < len(query_str) < 1000:
        raise InputError(description='Invalid query string length')

    # get all the messages in dms and channels that the user is in that contain the substring
    channels_list = get_user_channels(auth_user_id)
    dm_list = get_user_dms(auth_user_id)

    message_list = []

    # edit channel messages
    for channel_id in channels_list:
        for message_id in get_channel_messages(channel_id):
            message_content = get_message_by_id(message_id)['content']
            if query_str in message_content:
                message = {
                    'message_id': message_id,
                    'u_id': get_message_by_id(message_id)['author'],
                    'content': message_content,
                    'time_created': get_message_by_id(message_id)['time_created'],
                    'reacts': get_message_by_id(message_id)['reacts'],
                    'is_pinned': get_message_by_id(message_id)['is_pinned']
                }
                message_list.append(message)


    # edit dm messages
    for dm_id in dm_list:
        for message_id in get_messages_by_dm(dm_id):
            message_content = get_message_by_id(message_id)['content']
            if query_str in message_content:
                message = {
                    'message_id': message_id,
                    'u_id': get_message_by_id(message_id)['author'],
                    'content': message_content,
                    'time_created': get_message_by_id(message_id)['time_created'],
                    'reacts': get_message_by_id(message_id)['reacts'],
                    'is_pinned': get_message_by_id(message_id)['is_pinned']
                }
                message_list.append(message)
    
    return message_list