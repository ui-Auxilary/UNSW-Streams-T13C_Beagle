import pytest
import requests
import json

from src import config

'''
VALID_INPUT
    - Valid auth_user_id
    - Valid channel_id
    - Valid channel and user id however user not member of channel

VALID_OUTPUT
    - Return details of the channel
'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_user_and_channel():
    ## register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
                                                                            'email': 'hello@mycompany.com', 
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Firstname',
                                                                            'name_last': 'Lastname'
                                                                          })
    user_token = json.loads(register_data.text)['token']
    auth_user_id = json.loads(register_data.text)['auth_user_id']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', json={
                                                        'email': 'hello@mycompany.com',
                                                        'password': 'mypassword'
                                                        })

    ## create a channel with that user
    channel_data = requests.post(config.url + 'channels/create/v2', json={
                                                                            'token': user_token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                           })

    channel_id = json.loads(channel_data.text)['channel_id']
    return auth_user_id, channel_id, user_token

def test_simple_case(clear_data, create_user_and_channel):
    auth_user_id, channel_id, user_token = create_user_and_channel

    ## get the user data
    user_profile_data = requests.get(config.url + 'user/profile/v1', params={
                                                                        'token': user_token,
                                                                        'u_id': auth_user_id 
                                                                       })

    auth_user_profile = json.loads(user_profile_data.text)['user']

    ## get information about the channel
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                 'token': user_token,
                                                                                 'channel_id': channel_id
                                                                                })

    channel_detail = json.loads(channel_detail_data.text)

    channel_name = channel_detail['name']
    channel_members = channel_detail['all_members']
    channel_owners = channel_detail['owner_members']

    channel = {
        'channel_id': channel_id,
        'name': channel_name
    }

    ## get information about the channel
    channel_list_data = requests.get(config.url + 'channels/list/v2', params={
                                                                              'token': user_token,
                                                                             })

    channel_list = json.loads(channel_list_data.text)['channels']

    assert channel in channel_list
    assert auth_user_profile in channel_members
    assert auth_user_profile in channel_owners

def test_user_joins_channel(clear_data, create_user_and_channel):
    auth_user_id, channel_id, user_token = create_user_and_channel

    ## register another user
    register_data_2 = requests.post(config.url + 'auth/register/v2', json={ 
                                                                            'email': 'hello2@mycompany.com', 
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Firstname2',
                                                                            'name_last': 'Lastname2'
                                                                          })

    user_token_2 = json.loads(register_data_2.text)['token']

    ## second user joins the existing channel
    requests.post(config.url + 'channel/join/v2', json={
                                                        'token': user_token_2,
                                                        'channel_id': channel_id
                                                        })

    ## get the profile of both users
    user_profile_data = requests.get(config.url + 'user/profile/v1', params={
                                                                        'token': user_token,
                                                                        'u_id': auth_user_id 
                                                                       })

    user_2_profile_data = requests.get(config.url + 'user/profile/v1', params={
                                                                        'token': user_token_2,
                                                                        'u_id': auth_user_id 
                                                                       })

    auth_user_profile = json.loads(user_profile_data.text)['user']
    user_2_profile = json.loads(user_2_profile_data.text)['user']

    ## get information about the channel
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                 'token': user_token,
                                                                                 'channel_id': channel_id
                                                                                })

    channel_detail = json.loads(channel_detail_data.text)

    channel_name = channel_detail['name']
    channel_members = channel_detail['all_members']
    channel_owners = channel_detail['owner_members']

    channel = {
        'channel_id': channel_id,
        'name': channel_name
    }

    ## get list of channels
    channel_list_data = requests.get(config.url + 'channels/list/v2', params={
                                                                              'token': user_token,
                                                                             })

    channel_list = json.loads(channel_list_data.text)['channels']

    assert channel in channel_list
    assert auth_user_profile in channel_members
    assert user_2_profile in channel_members
    assert auth_user_profile in channel_owners

def test_invalid_token(clear_data, create_user_and_channel):
    _, channel_id, _ = create_user_and_channel
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                'token': "25",
                                                                                'channel_id': channel_id
                                                                                })
    assert channel_detail_data.status_code == 403

def test_invalid_channel_id(clear_data, create_user_and_channel):
    _, _, user_token= create_user_and_channel
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                'token': user_token,
                                                                                'channel_id': 25
                                                                                })
    assert channel_detail_data.status_code == 400

def test_user_not_channel_member(clear_data, create_user_and_channel):
    _, channel_id, _ = create_user_and_channel

    ## register user and get their user_id
    register_data_2 = requests.post(config.url + 'auth/register/v2', json={
                                                                            'email': 'hello2@mycompany.com', 
                                                                            'password': 'my2password',
                                                                            'name_first': 'First2name',
                                                                            'name_last': 'Last2name'
                                                                          })
    token_2 = json.loads(register_data_2.text)['token']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', json={
                                                        'email': 'hello2@mycompany.com',
                                                        'password': 'my2password'
                                                        })

    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                'token': token_2,
                                                                                'channel_id': channel_id
                                                                                })
    assert channel_detail_data.status_code == 403
