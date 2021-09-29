import pytest

from src.error import AccessError
from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1

'''
FUNCTIONALITY
- Lists all existing channels
    - empty channel_data
    - list_all_private_channels
    - multiple users make channels
    - list_channels_alt_id
    - duplciate_channel_name
RETURN TYPE
    - All channels and associated data
    { channels: [
        'channel_id': id,
        'name': name
    ]}

ACCESS ERROR
    - Invalid user_id or user does not exist
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

def test_valid_user_id(clear_data):
    with pytest.raises(AccessError):
        ## arbitrary user id (122)
        channels_create_v1(122, 'Channel_1', True)['channel_id']

def test_basic_case(clear_data, auth_register_and_login):
    ## register and get user ids
    user_id, user_id_2 = auth_register_and_login

    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']

    assert channels_listall_v1(user_id) == { 'channels': [
        {
            'channel_id': channel_id_1, 
            'name':'Channel_1'
        }
    ]}

def test_listall_duplicate_name(clear_data, auth_register_and_login):
    ## register and get user ids
    user_id, user_id_2 = auth_register_and_login

    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id_2, 'Channel_1', True)['channel_id']

    assert channels_listall_v1(user_id) == { 'channels': [
        {
            'channel_id': channel_id_1, 
            'name':'Channel_1'
        },
        {
            'channel_id': channel_id_2, 
            'name':'Channel_1'
        }
    ]}

def test_list_alt_user_id(clear_data, auth_register_and_login):
    user_id, user_id_2 = auth_register_and_login

    ## create channels and get their ids
    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id_2, 'Channel_2', True)['channel_id']
    channel_id_3 = channels_create_v1(user_id_2, 'Channel_3', False)['channel_id']
    
    ## checks the channels returned by channel list match
    assert channels_listall_v1(user_id_2) == {
        'channels': [
            {
                'channel_id': channel_id_1, 
                'name':'Channel_1'
            }, 
            {
                'channel_id': channel_id_2, 
                'name':'Channel_2'
            }, 
            {
                'channel_id': channel_id_3, 
                'name':'Channel_3'
            }
        ]
    }

def test_all_private_channels(clear_data, auth_register_and_login):
    ## get registered user ids
    user_id, user_id_2 = auth_register_and_login

    ## create a channel
    channel_id_1 = channels_create_v1(user_id, 'Channel_1', False)['channel_id']
    channel_id_2 = channels_create_v1(user_id_2, 'Channel_2', False)['channel_id']
    channel_id_3 = channels_create_v1(user_id, 'Channel_3', False)['channel_id']
    
    ## checks the channels returned by channel list match
    assert channels_listall_v1(user_id)['channels'] == [
            {
                'channel_id': channel_id_1, 
                'name':'Channel_1'
            }, 
            {
                'channel_id': channel_id_2, 
                'name':'Channel_2'
            }, 
            {
                'channel_id': channel_id_3, 
                'name':'Channel_3'
            }
        ]

def test_multiple_users_create_channel(clear_data, auth_register_and_login):
    ## get registered user ids
    user_id, user_id_2 = auth_register_and_login

    ## create multiple channels with different user_ids
    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id, 'Channel_2', False)['channel_id']
    channel_id_3 = channels_create_v1(user_id_2, 'Channel_3', False)['channel_id']

    ## check that all the channels listed in channel_data are the ones created
    assert channels_listall_v1(user_id)['channels'] == [
            {
                'channel_id': channel_id_1, 
                'name':'Channel_1'
            }, 
            {
                'channel_id': channel_id_2, 
                'name':'Channel_2'
            }, 
            {
                'channel_id': channel_id_3, 
                'name':'Channel_3'
            }
        ]

def test_empty_list(clear_data, auth_register_and_login):
    ## register and get user_ids
    user_id, user_id_2 = auth_register_and_login

    assert channels_listall_v1(user_id) == {'channels': []}

