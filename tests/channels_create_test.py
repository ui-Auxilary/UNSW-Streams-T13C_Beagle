import pytest
import requests
import json

from src import config
from src.error import InputError, AccessError

'''
VALID_INPUT
    - User ID is valid
    - 1 < len(channel name) < 20

FUNCTIONALITY
    - test public channel is public
    - test private channel is private
    - test user is in channel and user is owner    

'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_login_user():
    register_data = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'hello@mycompany.com', 
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Firstname',
                                                                            'name_last': 'Lastname'
                                                                            })

    auth_user_id = json.loads(register_data.text)['auth_user_id']
    user_token = json.loads(register_data.text)['token']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'hello@mycompany.com',
                                                        'password': 'mypassword'
                                                        })
    
    return auth_user_id, user_token

def test_user_id_exists(clear_data):
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(1),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    assert channel_data.status_code == 403

def test_valid_channel_length(clear_data, register_login_user):
    _, user_token = register_login_user

    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': user_token,
                                                                            'name': '',
                                                                            'is_public': True
                                                                            })

    assert channel_data.status_code == 400
    
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': user_token,
                                                                            'name': 'aoiwfbiaufgaiufgawiuofboawbfoawibfoiawb',
                                                                            'is_public': True
                                                                            })
    
    assert channel_data.status_code == 400

def test_public_channel_created(clear_data, register_login_user):
    _, user_token = register_login_user

    ## create a new channel
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': user_token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_id = json.loads(channel_data.text)['channel_id']

    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={'token': user_token,
                                                                                  'channel_id': channel_id
                                                                                  })
    
    channel_detail_name = json.loads(channel_detail_data.text)['name']
    channel_dict = {
                    'channel_id': channel_id,
                    'name': channel_detail_name
                    }

    channels_list_data = requests.get(config.url + 'channels/list/v2', params={'token': user_token})
    channel_lists = json.loads(channels_list_data.text)['channels']
    assert channel_dict in channel_lists

def test_private_channel_created(clear_data, register_login_user):
    user_id, user_token = register_login_user

    ## create a new channel
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': user_token,
                                                                            'name': 'channel_1',
                                                                            'is_public': False
                                                                            })
    
    channel_id = json.loads(channel_data.text)['channel_id']

    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={'token': user_token,
                                                                                  'channel_id': channel_id
                                                                                  })

    channel_detail_name = json.loads(channel_detail_data.text)['name']
    channel_dict = {
                    'channel_id': channel_id,
                    'name': channel_detail_name
                    }

    channels_list_data = requests.get(config.url + 'channels/list/v2', params={'token': user_token})
    channel_lists = json.loads(channels_list_data.text)['channels']

    assert channel_dict in channel_lists

def test_multiple_channel_created(clear_data, register_login_user):
    _, user_token = register_login_user

    ## register and log another user in
    register_data_2 = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'he@mycompany.com', 
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Firstname',
                                                                            'name_last': 'Lastname'
                                                                            })

    user_2_token = json.loads(register_data_2.text)['token']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'he@mycompany.com',
                                                        'password': 'mypassword'
                                                        })

    ## create two new channels
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': user_token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_data_2 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': user_2_token,
                                                                            'name': 'channel_1',
                                                                            'is_public': False
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    channel_detail_data_1 = requests.get(config.url + 'channel/details/v2', params={'token': user_token,
                                                                                  'channel_id': channel_id_1
                                                                                  })

    channel_detail_name_1 = json.loads(channel_detail_data_1.text)['name']
    channel_dict_1 = {
                    'channel_id': channel_id_1,
                    'name': channel_detail_name_1
                    }

    channel_detail_data_2 = requests.get(config.url + 'channel/details/v2', params={'token': user_2_token,
                                                                                  'channel_id': channel_id_2
                                                                                  })

    channel_detail_name_2 = json.loads(channel_detail_data_2.text)['name']
    channel_dict_2 = {
                    'channel_id': channel_id_2,
                    'name': channel_detail_name_2
                    }

    channels_list_data_1 = requests.get(config.url + 'channels/list/v2', params={'token': user_token})
    channels_list_data_2 = requests.get(config.url + 'channels/list/v2', params={'token': user_2_token})

    channel_lists_1 = json.loads(channels_list_data_1.text)['channels']
    channel_lists_2 = json.loads(channels_list_data_2.text)['channels']
    assert channel_dict_1 in channel_lists_1
    assert channel_dict_2 in channel_lists_2
