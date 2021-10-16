from src import auth
from src.error import InputError, AccessError
from src.other import check_user_exists, decode_token
from datetime import timezone, datetime

from datetime import datetime
from src.data_operations import (
    get_channel_ids,
    get_channel,
    add_message,
    get_message_ids,
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