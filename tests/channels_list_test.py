import pytest
import requests
import json

from src import config

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
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_login_user():
    register_data = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'owner@gmail.com', 
                                                                            'password': 'admin$only',
                                                                            'name_first': 'Owner',
                                                                            'name_last': 'Chan'
                                                                            })
    token = json.loads(register_data.text)['token']

    return token


def test_valid_auth_user(clear_data):
    channels_list_data = requests.get(config.url + 'channels/list/v2', params={'token': '129'})
    
    assert channels_list_data.status_code == 403

def test_list_duplicate_channel_name(clear_data, register_login_user):
    token = register_login_user

    ## create multiple channels with the same user_id
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_data_2 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': False
                                                                            })

    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']
    
    ## sorts the channels in alphabetical order
    channels_list_data = requests.get(config.url + 'channels/list/v2', params={'token': token
                                                                                })
    channels_list_data = json.loads(channels_list_data.text)

    ## check channels have the same name
    assert channels_list_data == {
        'channels': [
            {
                'channel_id': channel_id_1,
                'name': 'channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name': 'channel_1'
            }
        ]
    }

def test_list_private_channel(clear_data, register_login_user):
    token = register_login_user

    ## create multiple channels with the same user_id
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_data_2 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': token,
                                                                            'name': 'channel_2',
                                                                            'is_public': False
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']
    
    ## sorts the channels in alphabetical order
    channels_list_data = requests.get(config.url + 'channels/list/v2', params={'token': token
                                                                                })
    channels_list_data = json.loads(channels_list_data.text)
    ## get channels where user_id is owner
    assert channels_list_data == {
        'channels': [
            {
                'channel_id': channel_id_1,
                'name': 'channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name': 'channel_2'
            }
        ]
    }        

def test_user_member_multiple(clear_data, register_login_user):
    token = register_login_user

    ## register another user, and get their id
    register_data = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'user@gmail.com', 
                                                                            'password': 'member$only',
                                                                            'name_first': 'Peasant',
                                                                            'name_last': 'Kun'
                                                                            })

    token_2 = json.loads(register_data.text)['token']

    ## create multiple channels with the same user_id   
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_data_2 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': token,
                                                                            'name': 'channel_2',
                                                                            'is_public': True
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    ## user_2 joins channel
    requests.post(config.url + 'channel/join/v2', params={
                                                        'token': token_2,
                                                        'channel_id': channel_id_1
                                                        })
    requests.post(config.url + 'channel/join/v2', params={
                                                        'token': token_2,
                                                        'channel_id': channel_id_2
                                                        })

    ## sorts the channels in alphabetical order
    channels_list_data = requests.get(config.url + 'channels/list/v2', params={'token': token_2})
    channels_list_data = json.loads(channels_list_data.text)
    ## check both the owner and member are members
    assert channels_list_data == {
        'channels': [
            {
                'channel_id': channel_id_1,
                'name': 'channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name': 'channel_2'
            }
        ]
    }

def test_empty_channel_list(clear_data, register_login_user):
    token = register_login_user
    ## register user and get id
    user_id = register_login_user

    channels_list_data = requests.get(config.url + 'channels/list/v2', params={'token': token})
    channels_list_data = json.loads(channels_list_data.text)
    assert channels_list_data == {
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