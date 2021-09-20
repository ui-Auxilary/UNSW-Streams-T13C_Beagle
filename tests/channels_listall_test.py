import pytest

from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1

'''
FUNCTIONALITY
- Lists all existing channels
    - empty channel_data
    - list_all_private_channels
    - multiple users make channels

RETURN TYPE
    - All channels and associated data
    { channels: [
        'channel_id': id,
        'name': name
    ]}
'''

@pytest.fixture
def clear_data():
    clear_v1()

@pytest.fixture
def auth_register_and_login():
    ## register users
    auth_register_v1('owner@gmail.com', 'admin$only', 'Owner', 'Chan')
    user_id = auth_login_v1('owner@gmail.com', 'admin$only')['auth_user_id']
    auth_register_v1('peasant@gmail.com', 'peasant$only', 'Rice', 'Farmer')
    user_id_2 = auth_login_v1('peasant@gmail.com', 'peasant$only')['auth_user_id']

    return user_id, user_id_2

def test_basic_case(clear_data, auth_register_and_login):
    user_id, user_id_2 = auth_register_and_login

    ## create a channel
    channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channels_create_v1(user_id, 'Channel_2', True)['channel_id']
    channels_create_v1(user_id, 'Channel_3', True)['channel_id']
    
    ## checks the channels returned by channel list match
    assert channels_listall_v1 == {
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

def test_all_private_channels(clear_data, auth_register_and_login):
    user_id, user_id_2 = auth_register_and_login

    ## create a channel
    channels_create_v1(user_id, 'Channel_1', False)['channel_id']
    channels_create_v1(user_id_2, 'Channel_2', False)['channel_id']
    channels_create_v1(user_id, 'Channel_3', False)['channel_id']
    
    ## checks the channels returned by channel list match
    assert channels_listall_v1 == {
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

def test_multiple_users_create_channel(clear_data, auth_register_and_login):
    ## get registered user ids
    user_id, user_id_2 = auth_register_and_login

    ## create multiple channels with different user_ids
    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id, 'Channel_2', False)['channel_id']
    channel_id_3 = channels_create_v1(user_id_2, 'Channel_3', False)['channel_id']

    ## check that all the channels listed in channel_data are the ones created
    assert channels_list_v1(user_id) == {
        'channels':[
            {
                'channel_id': channel_id_1,
                'name': 'Channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name': 'Channel_2'
            },
            {
                'channel_id': channel_id_3,
                'name': 'Channel_3'
            }
        ]
    }

def test_empty_list(clear_data, auth_register_and_login):
    user_id = auth_register_and_login
    assert channels_listall_v1(user_id) == {'channels': []}