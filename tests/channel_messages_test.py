import pytest
import requests
import json

from src import config

'''
INVALID_INPUT
    - channel_id does not refer to a valid channel
    - start is greater than the total number of messages in the channel
    when there are no messages

ACCESS_ERROR
    - channel_id is valid and the authorised user is not a member of the channel
'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_user_and_channel():
    ## register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'hello@mycompany.com', 
                                                                            'password': 'mypassword',
                                                                            'name_first': 'Firstname',
                                                                            'name_last': 'Lastname'
                                                                            })
    token = json.loads(register_data.text)['token']
    auth_user_id = json.loads(register_data.text)['auth_user_id']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'hello@mycompany.com', 
                                                        'password': 'mypassword',
                                                        })

    ## create a channel with that user
    channel_data = requests.post(config.url + 'channels/create/v2', params={
                                                                            'token': token,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    
    channel_id = json.loads(channel_data.text)['channel_id']

    return auth_user_id, token, channel_id

def test_channel_messages_simple_case(clear_data, create_user_and_channel):
    _, token, channel_id = create_user_and_channel

    start = 0
    
    for i in range (0, 51):
        requests.post(config.url + 'message/send/v1', params={
                                                             'token': token,
                                                             'channel_id': channel_id,
                                                             'message': f"{i}"
                                                            })

    dm_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                        'token': token,
                                                                        'channel_id': channel_id,
                                                                        'start': start
                                                                      })


    channel_messages = json.loads(dm_data.text)['messages']
    dm_end = json.loads(dm_data.text)['end']

    assert len(channel_messages) == 49
    assert dm_end == 50

def test_irregular_start_integer(clear_data, create_user_and_channel):
    _, token, channel_id = create_user_and_channel
    start = 44

    for i in range (0, 50):
        requests.post(config.url + 'message/send/v1', params={
                                                              'token': token,
                                                              'channel_id': channel_id,
                                                              'message': f"{i}"
                                                             })

    dm_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                        'token': token,
                                                                        'channel_id': channel_id,
                                                                        'start': start
                                                                      })


    dm_messages = json.loads(dm_data.text)['messages']
    dm_end = json.loads(dm_data.text)['end']

    assert len(dm_messages) == 6
    assert dm_end == -1

def test_auth_user_id_exists(clear_data, create_user_and_channel):
    _, _, channel_id = create_user_and_channel
    start = 0

    ## auth_user does not exist
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': 'Iliketokens',
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })

    assert channel_messages_data.status_code == 403

def test_channel_messages_no_messages(clear_data, create_user_and_channel):
    _, token, channel_id = create_user_and_channel
    start = 0

    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                     'token': token,
                                                                                     'channel_id': channel_id,
                                                                                     'start': start
                                                                                    })
    channel_messages = json.loads(channel_messages_data.text)['messages']
    message_end = json.loads(channel_messages_data.text)['end']

    assert len(channel_messages) == 0
    assert channel_messages == []
    assert message_end == -1

def test_start_greater_than_total_messages(clear_data, create_user_and_channel):
    _, token, channel_id = create_user_and_channel
    start = 999

    ## start is greater than the total number of messages in the channel
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                     'token': token,
                                                                                     'channel_id': channel_id,
                                                                                     'start': start
                                                                                    })
    
    assert channel_messages_data.status_code == 400

def test_invalid_channel_id(clear_data, create_user_and_channel):
    _, token, _ = create_user_and_channel
    start = 0
    invalid_channel_id = 222

    ## invites user to a non-existent channel
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                     'token': token,
                                                                                     'channel_id': invalid_channel_id,
                                                                                     'start': start
                                                                                    })

    assert channel_messages_data.status_code == 400

def test_auth_user_not_member(clear_data, create_user_and_channel):
    _, _, channel_id = create_user_and_channel
    start = 0

    ## register new user that's not a member of the channel
    register_data = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'HELLO@mycompany.com', 
                                                                            'password': 'mypassword1',
                                                                            'name_first': 'Firstnamee',
                                                                            'name_last': 'Lastnamee'
                                                                          })
    
    token = json.loads(register_data.text)['token']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'HELLO@mycompany.com',
                                                        'password': 'mypassword1'
                                                        })

    ## checks that auth_user_id is not a member of the channel
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                     'token': token,
                                                                                     'channel_id': channel_id,
                                                                                     'start': start
                                                                                    })

    assert channel_messages_data.status_code == 403
    
## ACCESS AND INPUT ERROR OVERLAP TESTS
def test_user_not_member_and_invalid_start(clear_data, create_user_and_channel):
    _, _, channel_id = create_user_and_channel
    start = 10
    
    ## register new user that's not a member of the channel
    register_data = requests.post(config.url + 'auth/register/v2', params={ 
                                                                            'email': 'HELLO@mycompany.com', 
                                                                            'password': 'mypassword1',
                                                                            'name_first': 'Firstnamee',
                                                                            'name_last': 'Lastnamee'
                                                                          })
    
    token = json.loads(register_data.text)['token']

    ## logs in user
    requests.post(config.url + 'auth/login/v2', params={ 
                                                        'email': 'HELLO@mycompany.com',
                                                        'password': 'mypassword1'
                                                        })

    ## invalid start and user is not a member of the channel
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                     'token': token,
                                                                                     'channel_id': channel_id,
                                                                                     'start': start
                                                                                    })
    
    assert channel_messages_data.status_code == 403

def test_invalid_channel_and_invalid_user(clear_data):
    invalid_channel_id = 9384

    resp = requests.get(config.url + 'channel/messages/v2', params={
                                                                    'token': 'invalid_token',
                                                                    'channel_id': invalid_channel_id,
                                                                    'start': 0
                                                                   })

    assert resp.status_code == 403


