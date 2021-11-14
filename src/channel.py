'''
Control the properties and membership of channels

Functions:
    channel_invite_v1(auth_user_id: int, channel_id: int, u_id: int) -> dict
    channel_details_v1(auth_user_id: int, channel_id: int) -> dict
    channel_messages_v1(auth_user_id: int, channel_id: int, start: int) -> dict
    channel_join_v1(auth_user_id: int, channel_id: int) -> dict
'''

from typing_extensions import TypedDict
from src.error import InputError, AccessError
from src.other import decode_token
from src.data_operations import (
    get_message_ids,
    get_user_ids,
    get_channel_ids,
    get_channel, get_user,
    add_member_to_channel,
    get_message_by_id,
    get_messages_by_channel,
    add_message,
    add_notification,
    add_owner_to_channel,
    remove_owner_from_channel,
    remove_member_from_channel,
)
from datetime import timezone, datetime

# Type definitions


class channel_details(TypedDict):
    name: str
    owner_members: list
    all_members: list
    is_public: bool


class channel_messages(TypedDict):
    messages: list
    start: int
    end: int


def channel_invite_v1(token: str, channel_id: int, u_id: int) -> dict:
    '''
    A user invites another user and gives access to a channel and adds them to the channel

    Arguments:
        token        (str): token of the user that is being invited
        channel_id   (int): id of the channel user has been invited to
        u_id         (int): user id of the user being invited

    Exceptions:
        InputError: Occurs when:
                        - invited user does not exist
                        - channel does not exist
                        - the invited user is already a member
        AccessError: Occurs when:
                        - user does not have permission to invite another
                        - invalid auth_id

    Return Value:
        {}
    '''

    auth_user_id = decode_token(token)

    # check whether channel exists
    if channel_id not in get_channel_ids():
        raise InputError(description='Channel does not exist')

    # checks auth_user is a member of the channel
    if auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError(
            description='User is not authorised to invite new members')

    # checks u_id is valid
    if u_id not in get_user_ids():
        raise InputError(description='User does not exist')

    # check whether user is already member
    if u_id in get_channel(channel_id)['members']:
        raise InputError(description='New user is already existing member')

    # adds the new user to the channel
    dt = datetime.now()
    time_created = int(dt.timestamp())

    add_member_to_channel(channel_id, u_id, time_created)

    auth_user_handle = get_user(auth_user_id)['user_handle']
    channel_name = get_channel(channel_id)['name']
    add_notification(True, channel_id, u_id,
                     f"{auth_user_handle} added you to {channel_name}")

    return {
    }


def channel_details_v1(token: str, channel_id: int) -> channel_details:
    '''
    Generates all details of a selected channel such as channel name, the owners of the channel,
    all members of the channel, and whether the channel is public or private.

    Arguments:
        token        (str): an encoded token containing a user's id
        channel_id   (int): channel id of the selected channel

    Exceptions:
        InputError: Occurs when:
                        - channel_id does not exist
        AccessError: Occurs when:
                        - user is not a channel member
                        - invalid auth_id

    Return Value:
        { name           (str): channel's name
          owner_members (list): list of dicts with details of channel owners
          all_members   (list): list of dicts with details of channel members and owners
          is_public     (bool): True if channel is public else False }
    '''

    auth_user_id = decode_token(token)

    # check if channel_id is valid
    if channel_id not in get_channel_ids():
        raise InputError(description='Channel_id does not exist')

    # check whether user is in channel
    channel_info = get_channel(channel_id)
    channel_members = channel_info['members']

    if auth_user_id not in channel_members:
        raise AccessError(description='User is not channel member')

    # get the owner's information
    owners = []
    for owner_id in get_channel(channel_id)['owner']:
        owner_details = get_user(owner_id)
        owner_dict = {
            'u_id': owner_id,
            'email': owner_details['email_address'],
            'name_first': owner_details['first_name'],
            'name_last': owner_details['last_name'],
            'handle_str': owner_details['user_handle'],
            'profile_img_url': owner_details['image_url']
        }
        owners.append(owner_dict)

    # create list of dictionaries with member info
    member_info = []
    for member in channel_members:
        member_details = get_user(member)

        member_dict = {
            'u_id': member,
            'email': member_details['email_address'],
            'name_first': member_details['first_name'],
            'name_last': member_details['last_name'],
            'handle_str': member_details['user_handle'],
            'profile_img_url': member_details['image_url']
        }
        member_info.append(member_dict)

    return_dict = {
        'name': channel_info['name'],
        'owner_members': owners,
        'all_members': member_info,
        'is_public': channel_info['is_public']
    }

    return return_dict


def channel_messages_v1(token: str, channel_id: int, start: int) -> channel_messages:
    '''
    Retrieves data of up to 50 sent messages for pagination

    Arguments:
        token        (str): an encoded token containing a user's id
        channel_id   (int): id of the selected channel
        start        (int): location of where messages start from to be viewed

    Exceptions:
        InputError: Occurs when:
                        - channel id does not exist
                        - start exceeds number of total messages
        AccessError: Occurs when:
                        - user is not a member of the channel
                        - invalid auth_id

    Return Value:
        { messages (list): list of dicts with up to 50 past message details
          start     (int): index measuring how recent to search for messages
          end       (int): index of final message retrieved (-1 if final message) }
    '''
    auth_user_id = decode_token(token)

    # checks for invalid channel_id
    if channel_id not in get_channel_ids():
        raise InputError(description='Channel_id does not exist')

    # checks if auth_user_id is a channel member
    if auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError(description='User is not channel member')

    result_arr = []
    # Gets all the messages in the channel sorted from recent to old
    message_id_list = list(reversed(get_messages_by_channel(channel_id)))
    end = start + 50

    # checks that start does not exceed total messages
    if start > len(message_id_list):
        raise InputError(description='Start number exceeds total messages')

    for message_pos, message_id in enumerate(message_id_list):
        # if message in given range
        if start <= message_pos < end:
            message_info = get_message_by_id(message_id)

            # add message to message_list
            result_arr.append({
                'message_id': message_id,
                'u_id': message_info['author'],
                'message': message_info['content'],
                'time_created': message_info['time_created'],
                'reacts': message_info['reacts'],
                'is_pinned': message_info['is_pinned']
            })

        # if past 50 messages, then exit
        if message_pos == end - 1:
            break

    # checks if 50 messages are displayed
    if end > len(message_id_list) - 1:
        end = -1

    return {
        'messages': result_arr,
        'start': start,
        'end': end,
    }


def channel_join_v1(token: str, channel_id: int) -> dict:
    '''
    Adds user to a channel

    Arguments:
        auth_user_id (int): user id of the user
        channel_id   (int): id of the selected channel

    Exceptions:
        InputError: Occurs when:
                        - channel does not exist
                        - user is already a member
        AccessError: Occurs when:
                        - user does not have permission to join a private channel
                        - invalid auth_id

    Return Value:
        {}
    '''

    auth_user_id = decode_token(token)

    # check whether channel exists
    if channel_id not in get_channel_ids():
        raise InputError(description='Channel does not exist')

    # check whether user already member
    if auth_user_id in get_channel(channel_id)['members']:
        raise InputError(description='User is existing member')

    # check whether user has sufficient permissions to join
    if not get_channel(channel_id)['is_public']:
        print(get_user(auth_user_id)['global_owner'])
        if not get_user(auth_user_id)['global_owner']:
            raise AccessError(description='User cannot join private channel')

    # add them to channel
    dt = datetime.now()
    time_created = int(dt.timestamp())

    add_member_to_channel(channel_id, auth_user_id, time_created)

    return {
    }


def channel_leave_v1(token: str, channel_id: int) -> dict:
    '''
    Removes a member from the channel

    Arguments:
        token        (str): an encoded token containing a users id
        channel_id   (int): id of the selected channel

    Exceptions:
        InputError: Occurs when:
                        - channel does not exist
        AccessError: Occurs when:
                        - user is not already channel member
                        - invalid auth_id

    Return Value:
        {}
    '''
    auth_user_id = decode_token(token)

    # Invalid channel
    if channel_id not in get_channel_ids():
        raise InputError(description="Not a valid channel id")

    # Get list of owners and members in the channel
    channel_owner = get_channel(channel_id)['owner']
    channel_members = get_channel(channel_id)['members']

    # check if user exists in channel members
    if auth_user_id not in channel_members:
        raise AccessError(description="User is not a member of the DM")

    # check if user is the owner of the channel
    if auth_user_id in channel_owner:
        channel_owner.remove(auth_user_id)

    dt = datetime.now()
    time_created = int(dt.timestamp())

    # remove user from members in the channel
    remove_member_from_channel(channel_id, auth_user_id, time_created)

    return {}


def channel_addowner_v1(token: str, channel_id: int, u_id: int) -> dict:
    '''
    Promotes a channel member to owner

    Arguments:
        token        (str): an encoded token containing a users id
        channel_id   (int): id of the selected channel
        u_id         (int): user id of the user being made owner

    Exceptions:
        InputError: Occurs when:
                        - channel does not exist
                        - user does not exist
                        - user is a non-member
                        - user is already owner
        AccessError: Occurs when:
                        - authorised user is not channel owner
                        - invalid auth_id

    Return Value:
        {}
    '''
    auth_user_id = decode_token(token)

    # check whether channel exists
    if channel_id not in get_channel_ids():
        raise InputError(description='Channel does not exist')

    if auth_user_id not in get_channel(channel_id)['owner'] and not get_user(auth_user_id)['global_owner']:
        raise AccessError(
            description='Not sufficient permissions to add new owner')

    # check whether authorised user is a member of the channel
    if auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError(
            description='User does not have owner permissions in the channel')

    if u_id not in get_user_ids():
        raise InputError(description='u_id does not exist')

    # check whether user not a member of the channel
    if u_id not in get_channel(channel_id)['members']:
        raise InputError(description='User is not a member of channel')

    # check whether user already owner
    if u_id in get_channel(channel_id)['owner']:
        raise InputError(description='User is already owner of channel')

    add_owner_to_channel(u_id, channel_id)

    return {}


def channel_removeowner_v1(token: str, channel_id: int, u_id: int) -> dict:
    '''
    Removes user as channel owner

    Arguments:
        token        (str): an encoded token containing a users id
        channel_id   (int): id of the selected channel
        u_id         (int): user id of the user being removed as owner

    Exceptions:
        InputError: Occurs when:
                        - channel does not exist
                        - user does not exist
                        - user is not already owner
                        - user is the sole channel owner
        AccessError: Occurs when:
                        - authorised user is not channel owner
                        - invalid auth_id

    Return Value:
        {}
    '''
    # check for valid token
    auth_user_id = decode_token(token)

    # check whether channel exists
    if channel_id not in get_channel_ids():
        raise InputError(description='Channel does not exist')

    if auth_user_id not in get_channel(channel_id)['owner'] and not get_user(auth_user_id)['global_owner']:
        raise AccessError(
            description='Not sufficient permissions to remove an owner')

    # check whether authorised user is a member of the channel
    if auth_user_id not in get_channel(channel_id)['members']:
        raise AccessError(
            description='User does not have owner permissions in the channel')

    if u_id not in get_user_ids():
        raise InputError(description='u_id does not exist')

    # check whether user already owner
    if u_id not in get_channel(channel_id)['owner']:
        raise InputError(description='User is not an owner of channel')

    if len(get_channel(channel_id)['owner']) < 2:
        raise InputError(description='Cannot remove only owner')

    remove_owner_from_channel(u_id, channel_id)

    return {}
