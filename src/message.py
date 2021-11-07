from src.error import InputError, AccessError
from src.other import decode_token
from datetime import timezone, datetime

from datetime import datetime
from src.data_operations import (
    add_react,
    get_channel_ids,
    get_channel,
    get_channel_messages,
    add_message,
    get_user_channels,
    get_user_dms,
    get_dm,
    get_dm_ids,
    get_message_ids,
    get_messages_by_channel,
    get_message_by_id,
    edit_message,
    get_messages_by_dm,
    get_dm_messages,
    react_message,
    remove_message,
    get_user
)


def message_send_v1(token, channel_id, message):
    '''
    Sends a message into the channel

    Arguments:
        token        (str): an encoded token containing a users id
        channel_id   (int): id of the selected channel
        message      (str): content being sent into the channel

    Exceptions:
        InputError: Occurs when:
                        - channel does not exist
                        - message length is less than 1 character
                        - message length is over 1000 characters
        AccessError: Occurs when:
                        - user is not a channel member
                        - invalid auth_id

    Return Value:
        {message_id  (int): unique message_id for the content}
    '''
    auth_user_id = decode_token(token)

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

    # time created
    dt = datetime.now()
    time_created = int(dt.replace(tzinfo=timezone.utc).timestamp())
    
    '''
    'author'
            - 'content'
            - 'time_created'
            - 'reacts' [{ react_id, u_ids }]
            - 'is_pinned'
    '''
    add_message(True, int(auth_user_id), int(channel_id),
                int(message_id), message, time_created)

    return {
        'message_id': int(message_id)
    }


def message_edit_v1(token, message_id, message):
    '''
    Edits a pre-existing message

    Arguments:
        token        (str): an encoded token containing a users id
        message_id   (int): unique message_id for the content
        message      (str): content being sent into the channel

    Exceptions:
        InputError: Occurs when:
                        - message length is over 1000 characters
                        - message_id does not exist in the channel/dm that the user has joined
        AccessError: Occurs when:
                        - message was not sent by the authorised user
                        - message is not being edited by the channel/DM owner
                        - invalid auth_id

    Return Value:
        {}
    '''
    auth_user_id = decode_token(token)

    # check message_id is valid
    if message_id not in get_message_ids():
        raise InputError(description="Invalid message id")

    # find the channel where the message is located
    channel_id = get_message_by_id(message_id)['channel_created']
    is_channel = get_message_by_id(message_id)['is_channel']

    message_length = len(message)

    # assert the length of the message
    if message_length > 1000:
        raise InputError(description="Message over 1000 characters")

    message_author = get_message_by_id(message_id)['author']

    if is_channel:
        channel_owner = get_channel(channel_id)['owner']

        if message_author != auth_user_id and auth_user_id not in channel_owner and not get_user(auth_user_id)['global_owner']:
            raise AccessError(
                description="User does not have permissions to edit selected message")
    else:
        dm_owner = get_dm(channel_id)['owner']

        # global owners do not have dm_owner perms unless they are the creator
        if message_author != auth_user_id and auth_user_id not in dm_owner:
            raise AccessError(
                description="User does not have permissions to edit message")

    edit_message(is_channel, channel_id, message_id, message)

    return {}


def message_remove_v1(token, message_id):
    '''
    Removes message from the channel/DM it was sent from

    Arguments:
        token        (str): an encoded token containing a users id
        message_id   (int): unique message_id for the content

    Exceptions:
        InputError: Occurs when:
                        - message_id does not exist in the channel/dm that the user has joined                       
        AccessError: Occurs when:
                        - message was not sent by the authorised user
                        - message is not being edited by the channel/DM owner
                        - invalid auth_id

    Return Value:
        {}
    '''
    # check the token
    auth_user_id = decode_token(token)

    # check message_id is valid
    if message_id not in get_message_ids():
        raise InputError(description="Invalid message id")

    message_author = get_message_by_id(message_id)['author']
    is_channel = get_message_by_id(message_id)['is_channel']

    # find the channel where the message is located
    channel_id = get_message_by_id(message_id)['channel_created']

    if is_channel:
        channel_owner = get_channel(channel_id)['owner']

        if message_author != auth_user_id and auth_user_id not in channel_owner and not get_user(auth_user_id)['global_owner']:
            raise AccessError(
                description="User does not have permissions to remove message")
    else:
        dm_owner = get_dm(channel_id)['owner']

        # global owners do not have dm_owner perms unless they are the creator
        if message_author != auth_user_id and auth_user_id not in dm_owner:
            raise AccessError(
                description="User does not have permissions to remove message")

    remove_message(is_channel, channel_id, message_id)

    return {}

def message_react_v1(token, message_id, react_id):
    auth_user_id = decode_token(token)

    # check message_id is valid
    if message_id not in get_message_ids():
        raise InputError(description="Invalid message id")

    channel_ids = get_user_channels(auth_user_id)
    dm_ids = get_user_dms(auth_user_id)

    message_id_valid = False
    if any(message_id in get_channel_messages(channel) for channel in channel_ids) == True:
        message_id_valid = True
    if any(message_id in get_dm_messages(dm) for dm in dm_ids) == True:
        message_id_valid = True

    if message_id_valid == False:
        raise InputError(description="Not a valid message_id in any channels the user is in")

    # check if react_id is valid
    valid_react_ids = [1]
    if react_id not in valid_react_ids:
        raise InputError(description="Invalid react id")
        
    # checks if react_id exists in the message
    if len(get_message_by_id(message_id)['reacts']) < 1:
        add_react(auth_user_id, message_id, react_id)
    else:
        # checks if message has already been reacted from auth_user
        if auth_user_id in get_message_by_id(message_id)['reacts'][0]['u_ids']:
            raise InputError(description="User has already reacted with this react_id")

        react_message(auth_user_id, message_id, react_id)

    return {}