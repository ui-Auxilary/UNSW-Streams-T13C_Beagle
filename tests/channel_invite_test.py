import pytest
import requests
import json

from src import config

'''
INPUT_ERROR  
    - channel_id does not exist
    - u_id does not exist
    - u_id is already member of the channel
      
ACCESS_ERROR
    - the authorised user is not a member of the channel
'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_user_and_channel():
    ## register user, log them in and get their user_id
    register_data_1 = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'hello@mycompany.com', 
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Firstname',
                                                                            'name_last': 'Lastname'
                                                                          })
    token_1 = json.loads(register_data_1.text)['token']
    auth_user_id_1 = json.loads(register_data_1.text)['auth_user_id']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'hello@mycompany.com',
                                                        'password': 'mypassword'
                                                        })

    ## register user, log them in and get their user_id
    register_data_2 = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'sam@mycompany.com', 
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Samantha',
                                                                            'name_last': 'Tse'
                                                                          })

    auth_user_id_2 = json.loads(register_data_2.text)['auth_user_id']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                                    'email': 'sam@mycompany.com',
                                                                    'password': 'mypassword'
                                                                    })

    ## create a channel with first user
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': token_1,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                           })
    
    channel_id = json.loads(channel_data.text)['channel_id']

    return auth_user_id_1, auth_user_id_2, channel_id

def test_auth_id_exists(clear_data, create_user_and_channel):
    auth_user_id_1, auth_user_id_2, channel_id = create_user_and_channel

    ## create a channel with that user
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': str(auth_user_id_1),
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                           })
    channel_id = json.loads(channel_data.text)['channel_id']

    ## User that doesn't exist tries to invite user to channel
    channel_invite_data = requests.post(config.url + 'channels/invite/v2', params={
                                                            'token': str(128),
                                                            'channel_id': channel_id,
                                                            'u_id': auth_user_id_2
                                                            })

    assert channel_invite_data.status_code == 400

def test_invite_channel_simple_case(clear_data, create_user_and_channel):
    auth_user_id_1, auth_user_id_2, channel_id = create_user_and_channel

    requests.post(config.url + 'channels/invite/v2', params={
                                                            'token': str(auth_user_id_2),
                                                            'channel_id': channel_id,
                                                            'u_id': auth_user_id_2
                                                            })

    ## check that both users are members now
    channel_details_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                'token': str(auth_user_id_1),
                                                                                'channel_id': channel_id
                                                                                })
    assert channel_details_data['all_members'][0]['u_id'] in [auth_user_id_1, auth_user_id_2]
    assert channel_details_data['all_members'][1]['u_id'] in [auth_user_id_1, auth_user_id_2]

def test_invalid_channel_id(clear_data, create_user_and_channel):
    auth_user_id_1, auth_user_id_2, _ = create_user_and_channel
    invalid_channel_id = 222

    channel_detail_data = requests.post(config.url + 'channels/invite/v2', params={
                                                                                    'token': str(auth_user_id_1),
                                                                                    'channel_id': invalid_channel_id,
                                                                                    'u_id': auth_user_id_2
                                                                                    })
    
    assert channel_detail_data.status_code == 400

def test_invalid_user_id_invited(clear_data, create_user_and_channel):
    auth_user_id_1, _, channel_id = create_user_and_channel
    invalid_new_user_id = 222

    channel_invite_data = requests.post(config.url + 'channels/invite/v2', params={
                                                                                    'token': str(auth_user_id_1),
                                                                                    'channel_id': channel_id,
                                                                                    'u_id': invalid_new_user_id
                                                                                    })
    
    assert channel_invite_data.status_code == 400

def test_invited_user_existing_channel_member(clear_data, create_user_and_channel):
    _, auth_user_id_2, channel_id = create_user_and_channel

    # add user to channel
    requests.post(config.url + 'channel/join/v2', params={
                                                        'token': str(auth_user_id_2),
                                                        'channel_id': channel_id
                                                        })
    
    channel_invite_data = requests.post(config.url + 'channels/invite/v2', params={
                                                                                    'token': str(auth_user_id_2),
                                                                                    'channel_id': channel_id,
                                                                                    'u_id': auth_user_id_2
                                                                                    })

    assert channel_invite_data.status_code == 400

def test_auth_user_not_channel_member(clear_data, create_user_and_channel):
    _, _, channel_id = create_user_and_channel

    ## register user, log them in and get their user_id
    register_data_3 = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'HELLO@mycompany.com', 
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Firstname',
                                                                            'name_last': 'Lastname'
                                                                          })
    token_3 = json.loads(register_data_3.text)['token']
    auth_user_id_3 = json.loads(register_data_3.text)['auth_user_id']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'HELLO@mycompany.com',
                                                        'password': 'mypassword'
                                                        })

    channel_invite_data = requests.post(config.url + 'channels/invite/v2', params={
                                                                                    'token': token_3,
                                                                                    'channel_id': channel_id,
                                                                                    'u_id': auth_user_id_3
                                                                                    })

    ## checks that auth_user_id is not a member of the channel
    assert channel_invite_data.status_code == 400

## ACCESS AND INPUT ERROR OVERLAP TESTS
def test_access_and_input_error(clear_data, create_user_and_channel):
    auth_user_id, u_id, channel_id = create_user_and_channel

    ## user inviting is not a member of the channel, and inviting an invalid user
    channel_invite_data = requests.post(config.url + 'channels/invite/v2', params={
                                                                                    'token': str(u_id),
                                                                                    'channel_id': channel_id,
                                                                                    'u_id': 212
                                                                                    })
    assert channel_invite_data.status_code == 400
    
    ## user inviting is not a member of the channel, and inviting an existing channel member
    channel_invite_data = requests.post(config.url + 'channels/invite/v2', params={
                                                                                    'token': str(u_id),
                                                                                    'channel_id': channel_id,
                                                                                    'u_id': auth_user_id
                                                                                    })
    assert channel_invite_data.status_code == 400
