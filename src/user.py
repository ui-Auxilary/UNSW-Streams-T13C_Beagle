'''
Handles operations used to alter a user's properties

Functions:
    user_profile_sethandle(token: str, handle_str: str)
'''
import re
import requests
from PIL import Image
from src.error import InputError
from src.data_operations import (
    get_user_handles,
    edit_user,
    get_user,
    get_user_channels,
    get_user_dms,
    get_message_ids,
    get_channel_ids,
    get_dm_ids,
    get_message_ids,
    get_message_by_id,
    get_complete_user_ids,
    get_user_emails,
    add_user_profileimage,
    get_user_notifications,
    calculate_involvement_rate,
    update_user_stats,
    get_user_stats
)
from src.other import decode_token
from typing import Dict


def user_profile(token: str, user_id: int) -> dict:
    '''
    Update a user's first and last name

    Arguments:
        token        (str): an encoded token containing a users id
        name_first   (str): first name of user
        name_last    (str): last name of user

    Exceptions:
        InputError: Occurs when:
                        - length of name_first is less than 1 character
                        - length of name_first is over 1000 characters
                        - length of name_last is less than 1 character
                        - length of name_last is over 1000 characters
        AccessError: Occurs when:
                        - invalid auth_id

    Return Value:
        {}
    '''
    # check if valid token and decode it
    decode_token(token)

    # check that user_id is valid
    if user_id not in get_complete_user_ids():
        raise InputError(description='Invalid u_id')

    user_info = get_user(user_id)
    return {
        'user': {
            'u_id': user_id,
            'email': user_info['email_address'],
            'name_first': user_info['first_name'],
            'name_last': user_info['last_name'],
            'handle_str': user_info['user_handle'],
            'profile_img_url': user_info['image_url']
        }
    }


def user_profile_setname(token: str, first_name: str, last_name: str) -> dict:
    '''
    Update a user's email address

    Arguments:
        token        (str): an encoded token containing a users id
        email        (str): email of user

    Exceptions:
        InputError: Occurs when:
                        - invalid email entered
                        - email already in use
        AccessError: Occurs when:
                        - invalid auth_id

    Return Value:
        {}
    '''
    # check if valid token and decode it
    user_id = decode_token(token)

    # check that new handle is valid length and alphanumeric
    if not 1 <= len(first_name) <= 50:
        raise InputError(
            description='first name must be between 1 and 50 characters')
    elif not 1 <= len(last_name) <= 50:
        raise InputError(
            description='last name must be between 1 and 50 characters')

    # if the names are valid change them
    edit_user(user_id, 'first_name', first_name)
    edit_user(user_id, 'last_name', last_name)


def user_profile_setemail(token: str, email: str) -> dict:
    '''
    Update a user's handle

    Arguments:
        token        (str): an encoded token containing a users id
        user_handle  (str): unique alphanumeric handle for user

    Exceptions:
        InputError: Occurs when:
                        - length of user_handle is under 3 characters
                        - length of user_handle is over 20 characters
                        - user_handle contains non-alphanumeric characters
                        - user_handle already in use
        AccessError: Occurs when:
                        - invalid auth_id

    Return Value:
        {}

    '''
    # check if valid token and decode it
    user_id = decode_token(token)

    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.match(pattern, email):
        raise InputError(description='Invalid email address')

    # check that new handle is valid length and alphanumeric
    if email in get_user_emails():
        raise InputError(description='Email already taken')

    # if the email is valid change it
    edit_user(user_id, 'email_address', email)


def user_profile_sethandle(token: str, handle_str: str) -> None:
    # check if valid token and decode it
    user_id = decode_token(token)

    # check that new handle is valid length and alphanumeric
    if not 3 <= len(handle_str) <= 20:
        raise InputError(
            description='handle must be between 3 and 20 characters')

    if not handle_str.isalnum():
        raise InputError(description='handle must be alphanumeric')

    # check that handle is not already taken
    if handle_str in get_user_handles():
        raise InputError(description='handle already taken')

    # if the handle is valid then edit the user's handle
    edit_user(user_id, 'user_handle', handle_str)


def user_profile_uploadphoto_v1(token: str, img_url: str, x_start: int, y_start: int, x_end: int, y_end: int) -> dict:
    # check if valid token and decode it
    user_id = decode_token(token)

    if not img_url:
        raise InputError(description='URL cannot be empty')

    try:
        image_data = requests.get(img_url, stream=True)
    except Exception as e:
        raise InputError(description=e) from e

    if image_data.status_code != 200:
        raise InputError(description='Invalid url parsed')

    try:
        img = Image.open(image_data.raw)
    except Exception as err:
        raise InputError(description='Link provided is not an image') from err

    if img.format != 'JPEG':
        raise InputError(description='Image provided must be a jpg file!')

    # ensure dimensions are valid
    width, height = img.size
    if x_start > x_end or y_start > y_end:
        raise InputError(description='Invalid dimensions')
    if x_end < 0 or y_end < 0:
        raise InputError(description='Invalid dimensions')
    if x_start > width or y_start > height:
        raise InputError(description='Invalid dimensions')
    if x_end > width or y_end > height:
        raise InputError(description='Invalid dimensions')

    # crop the image
    cropped_image = img.crop((x_start, y_start, x_end, y_end))

    add_user_profileimage(user_id, cropped_image)

    return {}


def notifications_get_v1(token: str) -> Dict[str, list]:
    auth_user_id = decode_token(token)

    notifications_arr = []
    # Gets all the user's notifications
    notification_list = list(reversed(get_user_notifications(auth_user_id)))
    end = 20

    for index, notification in enumerate(notification_list):
        # if notification in given range
        if index < end:
            # add notification to notifications_arr
            notifications_arr.append({
                'channel_id': notification['channel_id'],
                'dm_id': notification['dm_id'],
                'notification_message': notification['content']
            })

        # if past 20 notifications, then exit
        else:
            break

    return {
        'notifications': notifications_arr
    }


def user_stats_v1(token: str) -> Dict[str, dict]:
    user_id = decode_token(token)

    update_user_stats(user_id, False, False, False)
    user_stats = get_user_stats(user_id)

    return {
        'user_stats': user_stats
    }
