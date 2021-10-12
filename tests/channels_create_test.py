import pytest
import requests
import json

from src import config
from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1, channels_list_v1

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

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'hello@mycompany.com',
                                                        'password': 'mypassword'
                                                        })
    
    return auth_user_id

def test_user_id_exists(clear_data):
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(1),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    assert channel_data.status_code == 400

def test_valid_channel_length(clear_data, register_login_user):
    user_id = register_login_user

    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': '',
                                                                            'is_public': True
                                                                            })

    assert channel_data.status_code == 400
    
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'aoiwfbiaufgaiufgawiuofboawbfoawibfoiawb',
                                                                            'is_public': True
                                                                            })
    
    assert channel_data.status_code == 400

def test_public_channel_created(clear_data, register_login_user):
    user_id = register_login_user

    ## create a new channel
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_id = json.loads(channel_data.text)['channel_id']

    channels_list_data = requests.get(config.url + 'channels/list/v2', params={'token': str(user_id)})

    assert channels_list_data['channels'][0]['channel_id'] == channel_id

def test_private_channel_created(clear_data, register_login_user):
    user_id = register_login_user

    ## create a new channel
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': False
                                                                            })
    
    channel_id = json.loads(channel_data.text)['channel_id']

    channels_list_data = requests.get(config.url + 'channels/list/v2', params={'token': str(user_id)})

    assert channels_list_data['channels'][0]['channel_id'] == channel_id

def test_multiple_channel_created(clear_data, register_login_user):
    user_id_1 = register_login_user

    ## register and log another user in
    register_data_2 = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'he@mycompany.com', 
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Firstname',
                                                                            'name_last': 'Lastname'
                                                                            })

    user_id_2 = json.loads(register_data_2.text)['auth_user_id']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'he@mycompany.com',
                                                        'password': 'mypassword'
                                                        })

    ## create two new channels
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id_1),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_data_2 = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id_2),
                                                                            'name': 'channel_1',
                                                                            'is_public': False
                                                                            })
    
    channel_id_1 = json.loads(channel_data.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    channels_list_data_1 = requests.get(config.url + 'channels/list/v2', params={'token': str(user_id_1)})
    channels_list_data_2 = requests.get(config.url + 'channels/list/v2', params={'token': str(user_id_2)})

    assert channels_list_data_1['channels'][0]['channel_id'] == channel_id_1
    assert channels_list_data_2['channels'][0]['channel_id'] == channel_id_2
