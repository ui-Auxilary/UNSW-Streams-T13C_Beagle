import pytest
import requests
import json

from src import config

'''
VALID INPUT
    - invalid channel_id
    - user already in channel

ACCESS ERROR
    - channel is private AND user is not GLOBAL owner

- test if user is global owner and channel is private

'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_login_users():
    ## register users, and logs them in
    register_user = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'hello@mycompany.com',
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Firstname',
                                                                            'name_last': 'Lastname'
                                                                           })

    register_user_2 = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'sam@mycompany.com',
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Samantha',
                                                                            'name_last': 'Tse'
                                                                           })

    auth_user_id = json.loads(register_user.text)['auth_user_id']
    auth_user_id_2 = json.loads(register_user_2.text)['auth_user_id']

    requests.post(config.url + 'auth/login/v2', params={
                                                        'email': 'hello@mycompany.com',
                                                        'password': 'mypassword',
                                                      })

    requests.post(config.url + 'auth/login/v2', params={
                                                        'email': 'sam@mycompany.com',
                                                        'password': 'mypassword',
                                                      })

    return auth_user_id, auth_user_id_2  

def test_user_id_exists(clear_data, register_login_users):
    user_id, _ = register_login_users

    ## create a channel with that user
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                           })

    channel_id = json.loads(channel_data.text)['channel_id']

    ## User that doesn't exist tries to join channel
    channel_join_data = requests.post(config.url + 'channel/join/v2', params={
                                                                            'token': str(258),
                                                                            'channel_id': channel_id
                                                                            })

    assert channel_join_data.status_code == 400

def test_invalid_channel_id(clear_data, register_login_users):
    user_id, _ = register_login_users

    channel_join_data = requests.post(config.url + 'channel/join/v2', params={
                                                                            'token': str(user_id),
                                                                            'channel_id': 234
                                                                            })

    assert channel_join_data.status_code == 400

def test_user_already_in_channel(clear_data, register_login_users):
    user_id, _ = register_login_users

    ## create a channel with that user
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                           })
    
    channel_id = json.loads(channel_data.text)['channel_id']

    channel_join_data = requests.post(config.url + 'channel/join/v2', params={
                                                                            'token': str(user_id),
                                                                            'channel_id': channel_id
                                                                            })

    assert channel_join_data.status_code == 400

def test_private_not_global_owner(clear_data, register_login_users):
    user_id, new_user_id = register_login_users

    ## create a channel with that user
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': False
                                                                           })
    
    channel_id = json.loads(channel_data.text)['channel_id']  

    channel_join_data = requests.post(config.url + 'channel/join/v2', params={
                                                                            'token': str(new_user_id),
                                                                            'channel_id': channel_id
                                                                            })

    assert channel_join_data.status_code == 400

def test_private_is_global_owner(clear_data, register_login_users):
    user_id, new_user_id = register_login_users

    ## create a channel with that user
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(new_user_id),
                                                                            'name': 'channel_1',
                                                                            'is_public': False
                                                                           })
    channel_id = json.loads(channel_data.text)['channel_id']

    requests.post(config.url + 'channel/join/v2', params={
                                                        'token': str(user_id),
                                                        'channel_id': channel_id
                                                        })
    
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                'token': str(new_user_id),
                                                                                'channel_id': channel_id
                                                                                })

    assert channel_detail_data['all_members'][0]['u_id'] in [user_id, new_user_id]
    assert channel_detail_data['all_members'][1]['u_id'] in [user_id, new_user_id]

@pytest.mark.skip('Cannot test')
def test_simple_case(clear_data, register_login_users):
    '''
    ## register users, log them in and get their user_id
    user_id, new_user_id = register_login_users

    ## create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', 'True')['channel_id']    

    ## get them to join the channel
    channel_join_v1(new_user_id, channel_id)

    ## get the database
    data_source = data_store.get()
    ## check that both users are members now
    assert data_source['channel_data'][channel_id]['members'] == [user_id, new_user_id]
    '''
    pass
