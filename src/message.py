from src import auth
from src.error import InputError, AccessError
from src.other import check_user_exists, decode_token
from datetime import timezone, datetime

from datetime import datetime
from src.data_operations import (
    get_channel_ids,
    get_channel,
    add_message,
    get_dm,
    get_message_ids,
    get_messages_by_channel,
    get_message_by_id,
    edit_message,
    get_messages_by_dm,
    remove_message,
    get_user
)

def message_send_v1(token, channel_id, message):
    '''
    Send a message from the authorised user to the channel specified by channel_id. 
    Note: Each message should have its own unique ID, i.e. no messages should share an ID with another message, even if that other message is in a different channel.

    InputError when:

        channel_id does not refer to a valid channel
        length of message is less than 1 or over 1000 characters

        AccessError when:

        channel_id is valid and the authorised user is not a member of the channel
    '''
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    if channel_id not in get_channel_ids():
        raise InputError(description="Invalid channel id")
    elif auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError(description="User is not a member of the channel")

    message_length = len(message)
    if message_length < 1:
        raise InputError(description="Message under 1 character")
    elif message_length > 1000:
        raise InputError(description="Message over 1000 characters")

    message_id = len(get_message_ids()) + 1

    ## time created
    dt = datetime(2015, 10, 19)
    time_created = int(dt.replace(tzinfo=timezone.utc).timestamp())

    add_message(True, int(auth_user_id), int(channel_id), int(message_id), message, time_created)
    
    return {
        'message_id': int(message_id)
    }

def message_edit_v1(token, message_id, message): 
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)
    
    ## check message_id is valid
    if message_id not in get_message_ids():
        raise InputError(description="Invalid message id")

    ## find the channel where the message is located
    channel_id = get_message_by_id(message_id)['channel_created']
    is_channel = get_message_by_id(message_id)['is_channel']

    if is_channel:
        channel_owner = get_channel(channel_id)['owner']
    else:
        channel_owner = get_dm(channel_id)['owner']

    message_length = len(message)

    ## assert the length of the message
    if message_length > 1000:
        raise InputError(description="Message over 1000 characters")

    message_author = get_message_by_id(message_id)['author']

    if message_author != auth_user_id and auth_user_id not in channel_owner and not get_user(auth_user_id)['global_owner']:
        raise AccessError(description="User does not have permissions to edit selected message")

    edit_message(is_channel, channel_id, message_id, message)

    return {}

def message_remove_v1(token, message_id): 
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## check message_id is valid
    if message_id not in get_message_ids():
        raise InputError(description="Invalid message id")

    message_author = get_message_by_id(message_id)['author']
    is_channel = get_message_by_id(message_id)['is_channel']

    ## find the channel where the message is located
    channel_id = get_message_by_id(message_id)['channel_created']

    if is_channel:
        channel_owner = get_channel(channel_id)['owner']
    else:
        channel_owner = get_dm(channel_id)['owner']

    if message_author != auth_user_id and auth_user_id not in channel_owner and not get_user(auth_user_id)['global_owner']:
        raise AccessError(description="User does not have permissions to remove message")

    remove_message(is_channel, channel_id, message_id)

    return {}