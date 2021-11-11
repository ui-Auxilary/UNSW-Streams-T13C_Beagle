import threading
from src.error import InputError, AccessError
from src.other import decode_token, check_valid_tag
from datetime import timezone, datetime

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
    get_message_by_id,
    get_message_ids,
    get_messages_by_channel,
    get_message_content,
    get_message_by_id,
    edit_message,
    get_messages_by_dm,
    get_dm_messages,
    react_message,
    pin_message,
    remove_message,
    get_user,
    add_notification,
    add_sendlater_id,
    add_dm_sendlater_id
)


def message_send_v1(token, channel_id, message, message_sendlater = 0):
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

    if message_sendlater != 0:
        message_id = message_sendlater
    else:
        message_id = len(get_message_ids()) + 1

    # time created
    dt = datetime.now()
    time_created = int(dt.timestamp())

    if "@" in message:
        tagged_user = check_valid_tag(message)
        if tagged_user:
            auth_user_handle = get_user(auth_user_id)['user_handle']
            channel_name = get_channel(channel_id)['name']
            add_notification(True, channel_id, tagged_user,
                             f"{auth_user_handle} tagged you in {channel_name}: {message[:20]}")

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

    if is_channel:
        channel_name = get_channel(channel_id)['name']
    else:
        channel_name = get_dm(channel_id)['name']

    if "@" in message:
        tagged_user = check_valid_tag(message)
        if tagged_user:
            auth_user_handle = get_user(auth_user_id)['user_handle']

            add_notification(is_channel, channel_id, tagged_user,
                             f"{auth_user_handle} tagged you in {channel_name}: {message[:20]}")

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

    dt = datetime.now()
    time_created = int(dt.timestamp())

    remove_message(is_channel, channel_id, message_id, time_created)

    return {}


def message_react_v1(token, message_id, react_id):
    '''
    Reacts to a message in a channel/DM

    Arguments:
        token        (str): an encoded token containing a users id
        message_id   (int): unique message_id for the content
        react_id     (int): id of the react type

    InputError when any of:
    - message_id is not a valid message within a channel or DM that the authorised user has joined
    - react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
    - the message already contains a react with ID react_id from the authorised user

    AccessError when any of:
        - invalid_id

    Return Value:
        {}
    '''
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
        raise InputError(
            description="Not a valid message_id in any channels the user is in")

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
            raise InputError(
                description="User has already reacted with this react_id")

        react_message(auth_user_id, message_id, react_id)

    # send notification
    is_channel = get_message_by_id(message_id)['is_channel']
    channel_id = get_message_by_id(message_id)['channel_created']

    if is_channel:
        channel_name = get_channel(channel_id)['name']
    else:
        channel_name = get_dm(channel_id)['name']

    author_id = get_message_by_id(message_id)['author']
    auth_user_handle = get_user(auth_user_id)['user_handle']
    add_notification(is_channel, channel_id, author_id,
                     f"{auth_user_handle} reacted to your message in {channel_name}")

    return {}


def message_unreact_v1(token, message_id, react_id):
    '''
    Unreacts message in the channel/DM it was sent from

    Arguments:
        token        (str): an encoded token containing a users id
        message_id   (int): unique message_id for the content
        react_id     (int): id of the react type

    InputError when any of:
    - message_id is not a valid message within a channel or DM that the authorised user has joined
    - react_id is not a valid react ID
    - the message does not contain a react with ID react_id from the authorised user

    AccessError when any of:
        - invalid_id

    Return Value:
        {}
    '''
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
        raise InputError(
            description="Not a valid message_id in any channels the user is in")

    # check if react_id is valid
    valid_react_ids = [1]

    if react_id not in valid_react_ids:
        raise InputError(description="Invalid react id")

    # checks if react_id exists in the message
    if len(get_message_by_id(message_id)['reacts']) < 1:
        raise InputError(description="User has not reacted with this react_id")
    else:
        # checks if message has already been reacted from auth_user
        if auth_user_id not in get_message_by_id(message_id)['reacts'][0]['u_ids']:
            raise InputError(
                description="User has not reacted with this react_id")

    react_message(auth_user_id, message_id, react_id)


def message_pin_v1(token, message_id):
    '''
    Pins message in the channel/DM it was sent from

    Arguments:
        token        (str): an encoded token containing a users id
        message_id   (int): unique message_id for the content

    InputError when any of: 
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        - the message is already pinned

    AccessError when:
        - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
        - invalid_token

    Return Value:
        {}
    '''
    auth_user_id = decode_token(token)

    # check message_id is valid
    if message_id not in get_message_ids():
        raise InputError(description="Invalid message id")

    channel_ids = get_user_channels(auth_user_id)
    dm_ids = get_user_dms(auth_user_id)
    message_id_valid = False

    if any(message_id in get_channel_messages(channel) for channel in channel_ids) == True:
        message_id_valid = True
        is_channel = True
    if any(message_id in get_dm_messages(dm) for dm in dm_ids) == True:
        message_id_valid = True

    if message_id_valid == False:
        raise InputError(
            description="Not a valid message_id in any channels the user is in")

    # check whether user has owner permissions in that channel
    channel_id = get_message_by_id(message_id)['channel_created']
    is_channel = get_message_by_id(message_id)['is_channel']
    
    if is_channel:
        if auth_user_id not in get_channel(channel_id)['owner'] and not get_user(auth_user_id)['global_owner']:
            raise AccessError(
                description='Not sufficient permissions to pin message')
    else:
        if auth_user_id not in get_dm(channel_id)['owner']:
            raise AccessError(
                description='Not sufficient permissions to pin message')

    # checks if message has been pinned
    if get_message_by_id(message_id)['is_pinned'] == True:
        raise InputError(description="Message has already been pinned")

    pin_message(message_id)

    return {}


def message_unpin_v1(token, message_id):
    '''
    Unpins message in the channel/DM it was sent from

    Arguments:
        token        (str): an encoded token containing a users id
        message_id   (int): unique message_id for the content

    InputError when any of: 
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        - the message is already pinned

    AccessError when:
        - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
        - invalid_token

    Return Value:
        {}
    '''
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
        raise InputError(
            description="Not a valid message_id in any channels the user is in")

    # check whether user has owner permissions in that channel
    channel_id = get_message_by_id(message_id)['channel_created']
    is_channel = get_message_by_id(message_id)['is_channel']

    if is_channel:
        if auth_user_id not in get_channel(channel_id)['owner'] and not get_user(auth_user_id)['global_owner']:
            raise AccessError(
                description='Not sufficient permissions to pin message')
    else:
        if auth_user_id not in get_dm(channel_id)['owner']:
            raise AccessError(
                description='Not sufficient permissions to unpin message')

    # checks if message has been pinned
    if get_message_by_id(message_id)['is_pinned'] == False:
        raise InputError(description="Message has not been pinned")

    pin_message(message_id)

    return {}


def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    Shares a message from a channel or dm to another channel or dm

    Arguments:
        token           (str): an encoded token containing a users id
        og_message_id   (int): unique message_id for the content
        message         (str): optional message the user can add to the shared message
        channel_id      (int): id of the channel the message is being shared to
        dm_id           (int): id of the dm the message is being shared to

    InputError when any of:      
    - both channel_id and dm_id are invalid
    - neither channel_id nor dm_id are -1        
    - og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    - length of message is more than 1000 characters
      
    AccessError when:      
    - The pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised 
      user has not joined the channel or DM they are trying to share the message to

    Return Value:
        {shared_message_id}
    '''
    user_id = decode_token(token)
       
    users_channels = get_user_channels(user_id)
    users_dms = get_user_dms(user_id)    
    
    if channel_id is -1 and dm_id is -1:
        raise InputError(description="Must share to valid dm or channel")
    
    if channel_id is not -1 and dm_id is not -1:
        raise InputError(description="User can only share to a channel or a dm")

    is_channel = False

    if dm_id == -1:
        channel_members = get_channel(channel_id)['members']
        is_channel = True
        send_to = channel_id

        if user_id not in channel_members:
            raise AccessError(description="User not in channel they are trying to share the message to")
    
    if channel_id == -1:
        dm_members = get_dm(dm_id)['members']
        send_to = dm_id
        
        if user_id not in dm_members:
            raise AccessError(description="User not in dm they are trying to share the message to")

    valid_message_ids = []
    for channel_ids in users_channels:
        channel_messages = get_channel_messages(channel_ids)
        for ch_msg in channel_messages:
            valid_message_ids.append(ch_msg)
    
    for dm_ids in users_dms:
        dm_messages = get_dm_messages(dm_ids)
        for dm_msg in dm_messages:
            valid_message_ids.append(dm_msg)
        
    if og_message_id not in valid_message_ids:
        raise InputError(description="Cannot share invalid message")
    
    if len(message) > 1000:
        raise InputError(description="Message must be less than or equal to 1000 characters")

    old_message = get_message_content(og_message_id)
    
    shared_message_id = len(get_message_ids()) + 1
    content = old_message + message
    dt = datetime.now()
    time_created = int(dt.timestamp())
    add_message(is_channel, user_id, send_to, shared_message_id, content, time_created)
        
    return {
              'shared_message_id': int(shared_message_id)
            }

def message_sendlater_v1(token, channel_id, message, time_sent):
    auth_user_id = decode_token(token)

    if channel_id not in get_channel_ids():
        raise InputError(description="Invalid channel id")
    elif auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError(description="User is not a member of the channel")

    # get current time
    dt = datetime.now(timezone.utc)
    time_created = int(dt.timestamp())

    # find how long in the future to send message
    length = time_sent - time_created

    if length < 0:
        raise InputError(description="Cannot send message to past")

    if len(message) > 1000:
        raise InputError(description="Message is too long")

    delayed_message_id = len(get_message_ids()) + 1
    add_sendlater_id(delayed_message_id)

    # set a timer, send the message when the standup ends
    timer = threading.Timer(length, message_send_v1,
                            (token, channel_id, message, delayed_message_id))
    timer.daemon = True
    timer.start()

    return {
        'message_id': delayed_message_id
    }

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    auth_user_id = decode_token(token)

    if dm_id not in get_dm_ids():
        raise InputError(description="Invalid dm id")
    elif auth_user_id not in get_dm(dm_id)['members']:
        raise AccessError(description="User is not a member of the dm")

    # get current time
    dt = datetime.now(timezone.utc)
    time_created = int(dt.timestamp())

    # find how long in the future to send message
    length = time_sent - time_created

    if length < 0:
        raise InputError(description="Cannot send message to past")

    if len(message) > 1000:
        raise InputError(description="Message is too long")

    delayed_message_id = len(get_dm_ids()) + 1
    add_dm_sendlater_id(delayed_message_id)

    # set a timer, send the message when the standup ends
    timer = threading.Timer(length, message_send_v1,
                            (token, dm_id, message, delayed_message_id))
    timer.daemon = True
    timer.start()

    return {
        'message_id': delayed_message_id
    }
