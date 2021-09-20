import pytest

from src.data_store import data_store
from src.error import InputError
from src.channel import channel_join_v1
from src.channels import channels_create_v1, channels_list_v1
from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1

'''
FUNCTIONALITY
    - list_private channels
    - user a part of multiple channels
    - user not a part of any channels
'''

@pytest.fixture
def clear_data():
    clear_v1()

def test_basic_case(clear_data):
    ## register user
    auth_register_v1('owner@gmail.com', 'admin$only', 'Owner', 'Chan')
    user_id = auth_login_v1('owner@gmail.com', 'admin$only')['auth_user_id']

    ## create a channel
    channels_create_v1(user_id, 'Channel_1', True)
    channels_create_v1(user_id, 'Channel_2', True)
    channels_create_v1(user_id, 'Channel_3', True)
    
    ## checks the channels returned by channel list match
    assert channels_list_v1(user_id) == {
        'channels': [
            {
                'channel_id': 1, 
                'name':'Channel_1'
            }, 
            {
                'channel_id': 2, 
                'name':'Channel_2'
            }, 
            {
                'channel_id': 3, 
                'name':'Channel_3'
            }
        ]
    }

def test_list_private_channel(clear_data):
    ## register user
    auth_register_v1('owner@gmail.com', 'admin$only', 'Owner', 'Chan')
    user_id = auth_login_v1('owner@gmail.com', 'admin$only')['auth_user_id']

    ## create multiple channels with the same user_id
    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id, 'Channel_2', False)['channel_id']
    
    ## get channels where user is owner
    assert channels_list_v1(user_id) == {
        'channels':[
            {
                'channel_id': channel_id_1,
                'name': 'Channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name': 'Channel_2'
            }
        ]
    }

def test_user_member_multiple(clear_data):
    ## register user
    auth_register_v1('owner@gmail.com', 'admin$only', 'Owner', 'Chan')
    user_id = auth_login_v1('owner@gmail.com', 'admin$only')['auth_user_id']

    auth_register_v1('user@gmail.com', 'member$only', 'Peasant', 'Kun')
    user_id_2 = auth_login_v1('user@gmail.com', 'member$only')['auth_user_id']

    ## create multiple channels with the same user_id   
    ## Admin makes a channel
    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id, 'Channel_2', True)['channel_id']

    ## User joins channel
    channel_join_v1(user_id_2, channel_id_1)
    channel_join_v1(user_id_2, channel_id_2)

    ## Check both the owner and member are members
    assert channels_list_v1(user_id_2) == {
        'channels':[
            {
                'channel_id': channel_id_1,
                'name': 'Channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name': 'Channel_2'
            }
        ]
    }

def test_empty_channel_list(clear_data):
    ## register user and get id
    auth_register_v1('owner@gmail.com', 'admin$only', 'Owner', 'Chan')
    user_id = auth_login_v1('owner@gmail.com', 'admin$only')['auth_user_id']

    assert channels_list_v1(user_id) == {
        'channels': []
    }
