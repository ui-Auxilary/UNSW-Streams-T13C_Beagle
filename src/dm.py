'''
from src.error import InputError, AccessError
from src.other import check_user_exists
from src.data_operations import (
    get_user_ids,
    get_channel_ids,
    get_channel, get_user,
    add_member_to_channel,
    get_message_by_id,
    get_messages_by_channel,
    add_message,
    edit_message,
    delete_message
)
'''

def dm_create(token, u_ids):
    dm_id = -1
    return dm_id


def dm_list(token):
    dms = []
    return dms


def dm_remove(token, dm_id):
    return None


def dm_details(token, dm_id):
    name = ""
    members = []
    return name, members


def dm_leave(token, dm_id):
    return None


def dm_messages(token, dm_id, start):
    messages = []
    end = -1
    return messages, start, end


def message_senddm(token, dm_id, message):
    message_id = -1
    return message_id
