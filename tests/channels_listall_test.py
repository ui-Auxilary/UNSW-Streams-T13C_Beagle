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
    register_data = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'owner@gmail.com', 
                                                                            'password': 'admin$only',
                                                                            'name_first': 'Owner',
                                                                            'name_last': 'Chan'
                                                                            })

    register_data_2 = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'peasant@gmail.com', 
                                                                            'password': 'peasant$only',
                                                                            'name_first': 'Rice',
                                                                            'name_last': 'Farmer'
                                                                            })

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'owner@gmail.com',
                                                        'password': 'admin$only'
                                                        })
    
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'peasant@gmail.com',
                                                        'password': 'peasant$only'
                                                        })
                                                        
    ## get user ids
    user_id = json.loads(register_data.text)['auth_user_id']
    user_id_2 = json.loads(register_data_2.text)['auth_user_id']

    return user_id, user_id_2

def test_valid_user_id(clear_data):
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(122),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    assert channel_data.status_code == 400

def test_basic_case(clear_data, auth_register_and_login):
    ## register and get user ids
    user_id, _ = auth_register_and_login

    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_id = json.loads(channel_data.text)['channel_id']

    assert requests.get(config.url + 'channels/listall/v2', params={'token': str(user_id)}) == { 'channels': [
        {
            'channel_id': channel_id, 
            'name':'channel_1'
        }
    ]}

def test_listall_duplicate_name(clear_data, auth_register_and_login):
    ## register and get user ids
    user_id, user_id_2 = auth_register_and_login

    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })

    channel_data_2 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id_2),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    ## sorts the channels in alphabetical order
    channels_listall_data = requests.get(config.url + 'channels/listall/v2', params={'token': str(user_id)
                                                                                })['channels'].sort(key = lambda x: x['name'])

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
    user_id, user_id_2 = auth_register_and_login

    ## create channels and get their ids
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })

    channel_data_2 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id_2),
                                                                            'name': 'channel_2',
                                                                            'is_public': True
                                                                            })

    channel_data_3 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id_2),
                                                                            'name': 'channel_3',
                                                                            'is_public': False
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']
    channel_id_3 = json.loads(channel_data_3.text)['channel_id']
    
    ## sorts the channels in alphabetical order
    channels_listall_data = requests.get(config.url + 'channels/listall/v2', params={'token': str(user_id_2)
                                                                                })['channels'].sort(key = lambda x: x['name'])

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
    user_id, user_id_2 = auth_register_and_login

    ## create a channel
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': False
                                                                            })

    channel_data_2 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id_2),
                                                                            'name': 'channel_2',
                                                                            'is_public': False
                                                                            })

    channel_data_3 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_3',
                                                                            'is_public': False
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']
    channel_id_3 = json.loads(channel_data_3.text)['channel_id']
    
    ## sorts the channels in alphabetical order
    channels_listall_data = requests.get(config.url + 'channels/listall/v2', params={'token': str(user_id)
                                                                                })['channels'].sort(key = lambda x: x['name'])

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
    user_id, user_id_2 = auth_register_and_login

    ## create multiple channels with different user_ids
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })

    channel_data_2 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_2',
                                                                            'is_public': False
                                                                            })

    channel_data_3 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id_2),
                                                                            'name': 'channel_3',
                                                                            'is_public': False
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']
    channel_id_3 = json.loads(channel_data_3.text)['channel_id']

    ## sorts the channels in alphabetical order
    channels_listall_data = requests.get(config.url + 'channels/listall/v2', params={'token': str(user_id)
                                                                                })['channels'].sort(key = lambda x: x['name'])
    
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
    user_id, _ = auth_register_and_login

    assert requests.get(config.url + 'channels/listall/v2', params={'token': str(user_id)}) == {
        'channels': []
    }

