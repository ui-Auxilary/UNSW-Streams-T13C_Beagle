import pytest
import requests
import json

from src import config

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
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def auth_register_and_login():
    ## register users
    register_data = requests.post(config.url + 'auth/register/v2', json={ 
                                                                            'email': 'owner@gmail.com', 
                                                                            'password': 'admin$only',
                                                                            'name_first': 'Owner',
                                                                            'name_last': 'Chan'
                                                                            })

    register_data_2 = requests.post(config.url + 'auth/register/v2', json={ 
                                                                            'email': 'peasant@gmail.com', 
                                                                            'password': 'peasant$only',
                                                                            'name_first': 'Rice',
                                                                            'name_last': 'Farmer'
                                                                            })

    token = json.loads(register_data.text)['token']
    token_2 = json.loads(register_data_2.text)['token']

    return token, token_2

def test_valid_user_id(clear_data):
    channel_data = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': str(122),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    assert channel_data.status_code == 403

def test_basic_case(clear_data, auth_register_and_login):
    ## register and get user ids
    token, _ = auth_register_and_login

    channel_data = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })

    channel_id = json.loads(channel_data.text)['channel_id']
    channel_list = requests.get(config.url + 'channels/listall/v2', params={'token': token})
    channel_list = json.loads(channel_list.text)

    assert channel_list == { 'channels': [
        {
            'channel_id': channel_id,
            'name':'channel_1'
        }
    ]}

def test_listall_duplicate_name(clear_data, auth_register_and_login):
    ## register and get user ids
    token, token_2 = auth_register_and_login

    channel_data = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })

    channel_data_2 = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token_2,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    ## sorts the channels in alphabetical order
    channels_listall_data = requests.get(config.url + 'channels/listall/v2', params={'token': token
                                                                                })

    channels_listall_data = json.loads(channels_listall_data.text)

    assert channels_listall_data == {
            'channels':[
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

def test_list_alt_user_id(clear_data, auth_register_and_login):
    token, token_2 = auth_register_and_login

    ## create channels and get their ids
    channel_data = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })

    channel_data_2 = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token_2,
                                                                            'name': 'channel_2',
                                                                            'is_public': True
                                                                            })

    channel_data_3 = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token_2,
                                                                            'name': 'channel_3',
                                                                            'is_public': False
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']
    channel_id_3 = json.loads(channel_data_3.text)['channel_id']
    
    ## sorts the channels in alphabetical order
    channels_listall_data = requests.get(config.url + 'channels/listall/v2', params={'token': token_2
                                                                                })

    channels_listall_data = json.loads(channels_listall_data.text)

    ## checks the channels returned by channel list match
    assert channels_listall_data == {
        'channels': [
            {
                'channel_id': channel_id_1,
                'name':'channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name':'channel_2'
            },
            {
                'channel_id': channel_id_3,
                'name':'channel_3'
            }
        ]
    }

def test_all_private_channels(clear_data, auth_register_and_login):
    ## get registered user ids
    token, token_2 = auth_register_and_login

    ## create a channel
    channel_data = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': False
                                                                            })

    channel_data_2 = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token_2,
                                                                            'name': 'channel_2',
                                                                            'is_public': False
                                                                            })

    channel_data_3 = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token,
                                                                            'name': 'channel_3',
                                                                            'is_public': False
                                                                            })

    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']
    channel_id_3 = json.loads(channel_data_3.text)['channel_id']

    ## sorts the channels in alphabetical order
    channels_listall_data = requests.get(config.url + 'channels/listall/v2', params={'token': token
                                                                                })

    channels_listall_data = json.loads(channels_listall_data.text)['channels']
    ## checks the channels returned by channel list match
    assert channels_listall_data == [
            {
                'channel_id': channel_id_1,
                'name':'channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name':'channel_2'
            },
            {
                'channel_id': channel_id_3,
                'name':'channel_3'
            }
        ]

def test_multiple_users_create_channel(clear_data, auth_register_and_login):
    ## get registered user ids
    token, token_2 = auth_register_and_login

    ## create multiple channels with different user_ids
    channel_data = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })

    channel_data_2 = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token,
                                                                            'name': 'channel_2',
                                                                            'is_public': False
                                                                            })

    channel_data_3 = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': token_2,
                                                                            'name': 'channel_3',
                                                                            'is_public': False
                                                                            })

    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']
    channel_id_3 = json.loads(channel_data_3.text)['channel_id']

    ## sorts the channels in alphabetical order
    channels_listall_data = requests.get(config.url + 'channels/listall/v2', params={'token': token
                                                                                })
    channels_listall_data = json.loads(channels_listall_data.text)['channels']
    ## check that all the channels listed in channel_data are the ones created
    assert channels_listall_data == [
            {
                'channel_id': channel_id_1,
                'name':'channel_1'
            },
            {
                'channel_id': channel_id_2,
                'name':'channel_2'
            },
            {
                'channel_id': channel_id_3,
                'name':'channel_3'
            }
        ]

def test_empty_list(clear_data, auth_register_and_login):
    ## register and get user_ids
    token, _ = auth_register_and_login

    channels_listall_data = requests.get(config.url + 'channels/listall/v2', params={'token': token})
    channels_listall_data = json.loads(channels_listall_data.text)
    assert channels_listall_data == {
        'channels': []
    }

