import threading
from src.error import InputError, AccessError
from src.other import decode_token
from datetime import timezone, datetime

from src.data_operations import (
    get_channel_ids, get_channel, set_active_standup, add_standup_message, get_user, add_message, get_message_ids, clear_message_pack)


def send_message_package(channel_id, auth_user_id, time_finish):
    # get message data for the channel
    message_pack = get_channel(channel_id)['standup_data']['message_package']
    message_content = '\n'.join(line for line in message_pack)
    message_id = len(get_message_ids()) + 1

    # add the message to the channel
    add_message(True, auth_user_id, channel_id,
                message_id, message_content, time_finish)

    # clear message_pack and set_active_standup to False
    set_active_standup(False, channel_id, time_finish)

    clear_message_pack(channel_id)


def standup_start_v1(token, channel_id, length):
    # check for valid token
    auth_user_id = decode_token(token)

    # check whether channel exists
    if channel_id not in get_channel_ids():
        raise InputError(description='Channel does not exist')

    # check whether authorised user is a member of the channel
    if auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError(
            description='User is not a member of the channel')

    # check if there is already an active standup
    if get_channel(channel_id)['standup_data']['is_active'] == True:
        raise InputError(
            description='There is an ongoing active standup')

    # check that the length of the standup is not negative
    if length < 0:
        raise InputError(description='Invalid standup duration')

    # get the time now, and find when the standup ends
    dt = datetime.utcnow()

    time_created = int(dt.replace(tzinfo=timezone.utc).timestamp())
    time_finish = time_created + length

    set_active_standup(True, channel_id, time_finish)

    # set a timer, send the message when the standup ends
    timer = threading.Timer(length, lambda: send_message_package(
        channel_id, auth_user_id, time_finish))
    timer.daemon = True
    timer.start()

    return {
        'time_finish': time_finish
    }


def standup_active_v1(token, channel_id):
    # check for valid token
    auth_user_id = decode_token(token)

    # check whether channel exists
    if channel_id not in get_channel_ids():
        raise InputError(description='Channel does not exist')

    # check whether authorised user is a member of the channel
    if auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError(
            description='User is not a member of the channel')

    is_active = get_channel(channel_id)['standup_data']['is_active']
    time_finished = get_channel(channel_id)['standup_data']['time_finish']

    return {
        'is_active': is_active,
        'time_finish': time_finished
    }


def standup_send_v1(token, channel_id, message):
    # check for valid token
    auth_user_id = decode_token(token)

    # check whether channel exists
    if channel_id not in get_channel_ids():
        raise InputError(description='Channel does not exist')

    # check whether authorised user is a member of the channel
    if auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError(
            description='User is not a member of the channel')

    # check if there is already an active standup
    if get_channel(channel_id)['standup_data']['is_active'] == False:
        raise InputError(
            description='No active standups to send a message to')

    # check valid message length
    if len(message) > 1000:
        raise InputError(description='Message exceeds valid length')

    # get a users handle and convert it to the message_package form
    user_handle = get_user(auth_user_id)['user_handle']
    standup_message = f"{user_handle}: {message}"

    add_standup_message(channel_id, standup_message)

    return {}
