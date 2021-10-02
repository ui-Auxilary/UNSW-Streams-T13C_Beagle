import pytest

from src.error import AccessError
from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1
from src.channel import channel_join_v1
from src.channels import channels_create_v1, channels_list_v1

'''
FUNCTIONALITY
    - list_private channels
    - list_duplicate_channel_name
    - user a part of multiple channels
    - user not a part of any channels

ACCESS ERROR
    - Invalid user_id
'''

@pytest.fixture
def clear_data():
    clear_v1()

@pytest.fixture
def register_login_user():
    ## register user
    auth_register_v1('owner@gmail.com', 'admin$only', 'Owner', 'Chan')

    ## log user in and get their id
    user_id = auth_login_v1('owner@gmail.com', 'admin$only')['auth_user_id']

    return user_id    

def test_valid_user(clear_data):
    with pytest.raises(AccessError):
        channels_list_v1(129)

def test_list_duplicate_channel_name(clear_data, register_login_user):
    user_id = register_login_user

    ## create multiple channels with the same user_id
    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id, 'Channel_1', False)['channel_id']
    
    ## sorts the channels in alphabetical order
    channels_list_v1(user_id)['channels'].sort(key = lambda x: x['name'])
    
    ## check channels have the same name
    assert channels_list_v1(user_id) == {
        'channels': [
            {
                'channel_id': channel_id_1,
                'name': 'Channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name': 'Channel_1'
            }
        ]
    }

def test_list_private_channel(clear_data, register_login_user):
    user_id = register_login_user

    ## create multiple channels with the same user_id
    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id, 'Channel_2', False)['channel_id']
    
    ## sorts the channels in alphabetical order
    channels_list_v1(user_id)['channels'].sort(key = lambda x: x['name'])

    ## get channels where user_id is owner
    assert channels_list_v1(user_id) == {
        'channels': [
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

def test_user_member_multiple(clear_data, register_login_user):
    user_id = register_login_user

    ## register another user, and get their id
    auth_register_v1('user@gmail.com', 'member$only', 'Peasant', 'Kun')
    user_id_2 = auth_login_v1('user@gmail.com', 'member$only')['auth_user_id']

    ## create multiple channels with the same user_id   
    channel_id_1 = channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id, 'Channel_2', True)['channel_id']

    ## user_2 joins channel
    channel_join_v1(user_id_2, channel_id_1)
    channel_join_v1(user_id_2, channel_id_2)

    ## sorts the channels in alphabetical order
    channels_list_v1(user_id_2)['channels'].sort(key = lambda x: x['name'])

    ## check both the owner and member are members
    assert channels_list_v1(user_id_2) == {
        'channels': [
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

def test_empty_channel_list(clear_data, register_login_user):
    ## register user and get id
    user_id = register_login_user

    assert channels_list_v1(user_id) == {
        'channels': []
    }

## Whitebox tests
@pytest.mark.skip('This is a whitebox test')
def test_basic_case(clear_data, register_login_user):
    '''
    ## register user
    user_id = register_login_user

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
    '''
    pass