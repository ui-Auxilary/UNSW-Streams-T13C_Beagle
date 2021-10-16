import pytest

from src import config
import requests
import json

'''
InputError when:
      
    - message_id does not refer to a valid message within a channel/DM that the authorised user has joined
      
AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      
    - the message was sent by the authorised user making this request
    - the authorised user has owner permissions in the channel/DM
'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_channel_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token
    token = json.loads(register_data.text)['token']

    # create a channel with that user
    create_channel_data = requests.post(config.url + 'channels/create/v2', params={'token': token,
                                                                         'name':  'channel_1',
                                                                         'is_public': True
                                                                         })

    channel_id = json.loads(create_channel_data.text)['channel_id']

    # stores a string
    message = "Hello, I don't know what I am doing. Send help. xoxo."

    # creates a message_id
    message_send_data = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                       'channel_id': channel_id,
                                                                       'message': message
                                                                       })
    message_id = json.loads(message_send_data.text)['message_id']

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'HELLO@mycompany.com',
                                                                           'password': 'MYpassword',
                                                                           'name_first': 'FirstNAME',
                                                                           'name_last': 'LastNAME'
                                                                           })

    # stores a token
    token2 = json.loads(register_data.text)['token']

    return token, channel_id, message_id, token2

@pytest.fixture
def create_dm_data():
    # register user, get their user_id and token
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token
    token = json.loads(register_data.text)['token']

    # register another user, get their user_id and token
    register_data_2 = requests.post(config.url + 'auth/register/v2', params={'email': 'bobby@mycompany.com',
                                                                           'password': 'samepassword',
                                                                           'name_first': 'Bobby',
                                                                           'name_last': 'Dillo'
                                                                           })

    # stores a token
    token_2 = json.loads(register_data_2.text)['token']
    user_id_2 = json.loads(register_data_2.text)['auth_user_id']

    # create a dm with that user
    create_dm_data = requests.post(config.url + 'dm/create/v1', params={'token': token,
                                                                        'u_ids':  [user_id_2],
                                                                       })

    dm_id = json.loads(create_dm_data.text)['dm_id']

    # stores a string
    message = "Hello, I don't know what I am doing. Send help. xoxo."

    # creates a message_id
    message_send_data = requests.post(config.url + 'message/senddm/v1', params={'token': token,
                                                                       'dm_id': dm_id,
                                                                       'message': message
                                                                       })
    message_id = json.loads(message_send_data.text)['message_id']

    return token, dm_id, message_id, token_2

def test_simple_case(clear_data, create_channel_data):
    token, channel_id, message_id, _ = create_channel_data
    # message is sent to a non-existent channel
    resp = requests.delete(config.url + 'message/remove/v1', params={'token': token,
                                                                     'message_id': message_id,
                                                                     })

    assert resp.status_code == 200

    ## get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                   })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    ## assert the target message_id no longer exists and is hence deleted
    assert any(('message_id', message_id) in msg.items() for msg in channel_messages) == False

def test_remove_dm_message(clear_data, create_dm_data):
    token, dm_id, _, _ = create_dm_data
    # creates a message_id
    message_send_data = requests.post(config.url + 'message/senddm/v1', params={'token': token,
                                                                              'dm_id': dm_id,
                                                                              'message': 'Hi everybody'
                                                                             })
    message_id = json.loads(message_send_data.text)['message_id']

    resp = requests.delete(config.url + 'message/remove/v1', params={'token': token,
                                                                     'message_id': message_id,
                                                                     })

    assert resp.status_code == 200

    ## get the messages in the channel
    dm_message_data = requests.get(config.url + 'dm/messages/v1', params={
                                                                          'token': token,
                                                                          'dm_id': dm_id,
                                                                          'start': 0
                                                                         })
    
    dm_messages = json.loads(dm_message_data.text)['messages']

    ## assert the target message_id no longer exists and is hence deleted
    assert any(('message_id', message_id) in msg.items() for msg in dm_messages) == False
    
def test_remove_channel_message(clear_data, create_channel_data):
    token, channel_id, _, _ = create_channel_data

    # create another channel with that user
    create_channel_data = requests.post(config.url + 'channels/create/v2', params={'token': token,
                                                                         'name':  'channel_1',
                                                                         'is_public': True
                                                                         })

    channel_id_2 = json.loads(create_channel_data.text)['channel_id']

    # send_messages to different channels
    message_send_data = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                              'channel_id': channel_id_2,
                                                                              'message': 'Hi everybody'
                                                                             })
    message_id = json.loads(message_send_data.text)['message_id']

    message_send_data_2= requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                              'channel_id': channel_id,
                                                                              'message': 'Hi everybody'
                                                                             })
    message_id_2 = json.loads(message_send_data_2.text)['message_id']

    ## get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                   })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    resp = requests.delete(config.url + 'message/remove/v1', params={'token': token,
                                                                     'message_id': message_id_2,
                                                                     })

    assert resp.status_code == 200

    ## get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                   })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    ## get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                   })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    ## assert the target message_id no longer exists and is hence deleted
    assert any(('message_id', message_id) in msg.items() for msg in channel_messages) == False

def test_remove_multiple_channel_messages(clear_data, create_channel_data):
    token, channel_id, message_id, _ = create_channel_data

     # send_messages to different channels
    message_send_data = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                              'channel_id': channel_id,
                                                                              'message': 'Hi everybody2'
                                                                             })
    message_id_1 = json.loads(message_send_data.text)['message_id']

    message_send_data_2= requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                              'channel_id': channel_id,
                                                                              'message': 'Hi everybody'
                                                                             })
    message_id_2 = json.loads(message_send_data_2.text)['message_id']

    resp = requests.delete(config.url + 'message/remove/v1', params={'token': token,
                                                                     'message_id': message_id_1,
                                                                     })

    assert resp.status_code == 200

    resp = requests.delete(config.url + 'message/remove/v1', params={'token': token,
                                                                     'message_id': message_id_2,
                                                                     })

    assert resp.status_code == 200

     ## get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                   })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    ## assert the target message_id no longer exists and is hence deleted
    assert any(('message_id', message_id) in msg.items() for msg in channel_messages) == True
    assert any(('message_id', message_id_1) in msg.items() for msg in channel_messages) == False
    assert any(('message_id', message_id_2) in msg.items() for msg in channel_messages) == False

def test_invalid_message_id(clear_data, create_channel_data):
    token, _, _, _ = create_channel_data
    invalid_message_id = 7667

    resp = requests.delete(config.url + 'message/remove/v1', params={'token': token,
                                                                     'message_id': invalid_message_id,
                                                                     })

    assert resp.status_code == 400


def test_auth_user_not_member(clear_data, create_channel_data):
    _, _, message_id, token2 = create_channel_data

    resp = requests.delete(config.url + 'message/remove/v1', params={'token': token2,
                                                                     'message_id': message_id,
                                                                     })

    assert resp.status_code == 403


def test_auth_user_not_channel_owner(clear_data, create_channel_data):
    _, channel_id, message_id, token2 = create_channel_data

    requests.post(config.url + 'channel/join/v2', params={'token': token2,
                                                          'channel_id': channel_id,
                                                          })

    resp = requests.delete(config.url + 'message/remove/v1', params={'token': token2,
                                                                     'message_id': message_id,
                                                                     })

    assert resp.status_code == 403

def test_both_invalid_user_and_message_id(clear_data, create_channel_data):
    _, _, _, _ = create_channel_data
    invalid_message_id = 7667

    resp = requests.delete(config.url + 'message/remove/v1', params={'token': 'invalid_token',
                                                                     'message_id': invalid_message_id,
                                                                     })

    assert resp.status_code == 403
