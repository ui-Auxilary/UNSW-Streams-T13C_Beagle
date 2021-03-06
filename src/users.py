'''
Handles high level program-wide user functionality

Functions:
    users_all(token: str) -> dict
'''

from typing import Dict, List
from typing_extensions import TypedDict
from src.error import InputError
from src.data_operations import (
    get_user_handles,
    edit_user,
    get_user,
    get_user_ids,
    get_dm_ids,
    get_dm,
    get_channel_ids,
    get_channel,
    get_message_ids,
    calculate_utilization_rate,
    get_workspace_stats,
    update_workspace_stats
)
from src.other import decode_token


class users_all_dict(TypedDict):
    user: List[dict]


def users_all(token: str) -> users_all_dict:
    '''
    Returns a list of all users, including user ids, emails, first name, 
    last name and user handle.

    Arguments:
        token        (str): an encoded token containing a users id

    Exceptions:
        InputError: Occurs when:
                        - auth_id does not refer to a valid user
        AccessError: Occurs when:
                        - invalid auth_id

    Return Value:
        {user             (list): contains dictionary of information of each user
            {u_id          (int): unique u_id for each user
             email         (str): email of user
             name_first    (str): first name of user
             name_last     (str): last name of user
             user_handle   (str): unique alphanumeric handle for user
            }
        }
    '''
    user_id = decode_token(token)

    users = {'users': []}

    for user_id in get_user_ids():
        user_info = get_user(user_id)
        users['users'].append({
            'u_id': user_id,
            'email': user_info['email_address'],
            'name_first': user_info['first_name'],
            'name_last': user_info['last_name'],
            'handle_str': user_info['user_handle'],
            'profile_img_url': user_info['image_url']
        })

    return users


def users_stats_v1(token: str) -> Dict[str, dict]:
    '''
    Gets the workplace stats

    Arguments:
        token        (str): an encoded token containing a users id

    Exceptions:
        AccessError: Occurs when:
                        - invalid auth_id

    Return Value:
        {workspace_stats        (dict): contains the stats of the workspace
            {channels_exist     (int): number of channels user has joined
            dms_exist           (int): number of dms user has joined
            messages_exist      (int): number of messages user has sent
            utilization_rate    (float): the rate the user is involved in the platform
            }
        }
    '''
    decode_token(token)

    update_workspace_stats(False, False, False)
    workspace_stats = get_workspace_stats()

    return {
        'workspace_stats': workspace_stats
    }
