import pytest

import requests
from src import config
import json

'''
Test for when new message is empty

InputError when any of:

    - length of message is over 1000 characters
    - message_id does not refer to a valid message within a channel/DM that the authorised user has joined
      
AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      
    - the message was sent by the authorised user making this request
    - the authorised user has owner permissions in the channel/DM
'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
                                                                           'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                          })

    # stores a token
    token = json.loads(register_data.text)['token']
    auth_user_id = json.loads(register_data.text)['auth_user_id']

    # create a channel with that user
    channel_create_data = requests.post(config.url + 'channels/create/v2', json={
                                                                                   'token': token,
                                                                                   'name': 'channel_1',
                                                                                   'is_public': True
                                                                                  })

    channel_id = json.loads(channel_create_data.text)['channel_id']

    # register another user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
                                                                           'email': 'HELLO@mycompany.com',
                                                                           'password': 'MYpassword',
                                                                           'name_first': 'FirstNAME',
                                                                           'name_last': 'LastNAME'
                                                                          })

    # stores a token
    token2 = json.loads(register_data.text)['token']

    # add user_2 to the channel
    requests.post(config.url + 'channel/join/v2', json={
                                                          'token': token2,
                                                          'channel_id': channel_id
                                                         })
    # stores a string
    old_message = "Hello, I don't know what I am doing. Send help. xoxo."

    # user_2 sends a message
    message_send_data = requests.post(config.url + 'message/send/v1', json={
                                                                              'token': token2,
                                                                              'channel_id': channel_id,
                                                                              'message': old_message
                                                                             })
                                                                    
    message_id = json.loads(message_send_data.text)['message_id']

    ## send random messages
    for message in range(0, 5):
        message_send_data = requests.post(config.url + 'message/send/v1', json={
                                                                                  'token': token,
                                                                                  'channel_id': channel_id,
                                                                                  'message': f"This is message:{message}"
                                                                                 })

    return token, message_id, channel_id, auth_user_id, token2

@pytest.fixture
def create_dm_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
                                                                           'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                          })

    # stores a token
    token = json.loads(register_data.text)['token']
    auth_user_id = json.loads(register_data.text)['auth_user_id']

    # register another user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
                                                                           'email': 'HELLO@mycompany.com',
                                                                           'password': 'MYpassword',
                                                                           'name_first': 'FirstNAME',
                                                                           'name_last': 'LastNAME'
                                                                          })

    # stores a token
    token2 = json.loads(register_data.text)['token']
    user_2_id = json.loads(register_data.text)['auth_user_id']

    # create a dm with that user
    dm_create_data = requests.post(config.url + 'dm/create/v1', json={
                                                                        'token': token,
                                                                        'u_ids': [user_2_id]
                                                                       })

    dm_id = json.loads(dm_create_data.text)['dm_id']

    # stores a string
    old_message = "Hello, I don't know what I am doing. Send help. xoxo."

    # user_2 sends a message
    message_send_data = requests.post(config.url + 'message/senddm/v1', json={
                                                                              'token': token2,
                                                                              'dm_id': dm_id,
                                                                              'message': old_message
                                                                             })
                                                                    
    message_id = json.loads(message_send_data.text)['message_id']

    ## send random messages
    for message in range(0, 5):
        message_send_data = requests.post(config.url + 'message/senddm/v1', json={
                                                                                  'token': token,
                                                                                  'dm_id': dm_id,
                                                                                  'message': f"This is message:{message}"
                                                                                 })

    return token, message_id, dm_id, auth_user_id, token2

def test_simple_case(clear_data, create_data):
    _, message_id, channel_id, _, token2 = create_data

    ## edited string
    new_message = "I want to have a dalgona coffee biscuit"

    ## get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token2,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                    })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    ## check message_id exists, but edited message does not exist in the channel
    assert any(('message_id', message_id) in msg.items() for msg in channel_messages) == True
    assert any(('message', new_message) in msg.items() for msg in channel_messages) == False

    ## user_2 edits their own message
    requests.put(config.url + 'message/edit/v1', json={
                                                         'token': token2,
                                                         'message_id': message_id,
                                                         'message': new_message
                                                        })
    
    ## get the messages in the channel again
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token2,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                   })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    assert any(('message_id', message_id) in msg.items() for msg in channel_messages) == True
    assert any(('message', new_message) in msg.items() for msg in channel_messages) == True

def test_edit_dm_message(clear_data, create_dm_data):
    _, message_id, dm_id, _, token2 = create_dm_data

    ## edited string
    new_message = "I want to have a dalgona coffee biscuit"

    ## get the messages in the channel
    dm_message_data = requests.get(config.url + 'dm/messages/v1', params={
                                                                           'token': token2,
                                                                           'dm_id': dm_id,
                                                                           'start': 0
                                                                         })
    
    dm_messages = json.loads(dm_message_data.text)['messages']

    ## check message_id exists, but edited message does not exist in the dm
    assert any(('message_id', message_id) in msg.items() for msg in dm_messages) == True
    assert any(('message', new_message) in msg.items() for msg in dm_messages) == False

    ## user_2 edits their own message
    requests.put(config.url + 'message/edit/v1', json={
                                                         'token': token2,
                                                         'message_id': message_id,
                                                         'message': new_message
                                                        })
    
    ## get the messages in the dm again
    dm_message_data = requests.get(config.url + 'dm/messages/v1', params={
                                                                           'token': token2,
                                                                           'dm_id': dm_id,
                                                                           'start': 0
                                                                         })
    
    dm_messages = json.loads(dm_message_data.text)['messages']

    assert any(('message_id', message_id) in msg.items() for msg in dm_messages) == True
    assert any(('message', new_message) in msg.items() for msg in dm_messages) == True

def test_empty_case(clear_data, create_data):
    _, message_id, channel_id, _, token2 = create_data
    new_message = ""

    ## get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token2,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                   })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    ## assert the target message_id exists
    assert any(('message_id', message_id) in msg.items() for msg in channel_messages) == True

    ## editing the target message_id to an empty string
    requests.put(config.url + 'message/edit/v1', json={
                                                         'token': token2,
                                                         'message_id': message_id,
                                                         'message': new_message
                                                        })
    
    ## get the messages in the channel again
    channel_message_data_2 = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token2,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                   })
    
    channel_messages = json.loads(channel_message_data_2.text)['messages']

    ## assert the target message_id no longer exists and is hence deleted
    assert any(('message_id', message_id) in msg.items() for msg in channel_messages) == False


def test_edited_message_length_over_thousand_chars(clear_data, create_data):
    token, message_id, _, _, _ = create_data

    new_message = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam nec sagittis sem, id aliquet est. Maecenas dignissim gravida enim at vehicula,\
                Vestibulum non ullamcorper ante. Integer pellentesque placerat urna et mollis. Donec ornare, nisl id fringilla suscipit, diam diam viverra nibh, \
                aliquet lacinia diam ipsum ac nunc. Suspendisse aliquet dolor pretium mi ornare, non egestas purus tempus. Proin ut eros venenatis, vestibulum nunc at, pretium orci,\
                Quisque convallis purus feugiat nisl fermentum euismod. Nunc ornare ultricies leo sit amet vehicula. Sed at sem nibh. Integer pellentesque ac libero ac semper.\
                Vestibulum laoreet blandit felis, ac mattis erat dignissim vitae. In ut quam at urna placerat ultricies. Pellentesque nibh velit, interdum sit amet risus sed,\
                mollis sagittis nulla. Suspendisse leo justo, congue a varius vitae, venenatis at ipsum. Nunc porttitor velit et porttitor pretium. Duis in lacus et lorem feugiat,\
                cursus pulvinar non augue. Morbi non est nibh. Sed non tincidunt leo, non condimentum felis. Nunc mattis rutrum fringilla. Morbi ultricies ornare felis, at vulputate risus\
                mollis sed. Sed a dapibus neque, Etiam blandit egestas erat eget rutrum. Nunc scelerisque nulla est, vehicula lacinia leo dapibus quis. Duis eleifend diam ipsum, vitae \
                pretium lorem euismod sed. Duis vel'

    message_edit_data = requests.put(config.url + 'message/edit/v1', json={
                                                                             'token': token,
                                                                             'message_id': message_id,
                                                                             'message': new_message
                                                                            })
    assert message_edit_data.status_code == 400

def test_invalid_message_id(clear_data, create_data):
    token, _, _, new_message, _ = create_data
    invalid_message_id = 3248

    resp = requests.put(config.url + 'message/edit/v1', json={
                                                                'token': token,
                                                                'message_id': invalid_message_id,
                                                                'message': new_message
                                                               })
    assert resp.status_code == 400


def test_auth_user_not_member(clear_data, create_data):
    _, message_id, _, _,_ = create_data

    resp = requests.put(config.url + 'message/edit/v1', json={
                                                                'token': 'invalid_token',
                                                                'message_id': message_id,
                                                                'message': 'oogabooga'
                                                               })
    assert resp.status_code == 403

def test_owner_edits_user_message(clear_data, create_data):
    token, message_id, channel_id, _, token2 = create_data

    ## edited string
    new_message = "Impasta edits heheheheheehehehehh"

    ## get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token2,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                    })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    ## check message_id exists, but edited message does not exist in the channel
    assert any(('message_id', message_id) in msg.items() for msg in channel_messages) == True
    assert any(('message', new_message) in msg.items() for msg in channel_messages) == False

    ## Owner edits user_2's message
    owner_edit = requests.put(config.url + 'message/edit/v1', json={
                                                                      'token': token,
                                                                      'message_id': message_id,
                                                                      'message': new_message
                                                                     })
                
    assert owner_edit.status_code == 200

    ## get the messages in the channel again
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
                                                                                    'token': token2,
                                                                                    'channel_id': channel_id,
                                                                                    'start': 0
                                                                                   })
    
    channel_messages = json.loads(channel_message_data.text)['messages']

    assert any(('message_id', message_id) in msg.items() for msg in channel_messages) == True
    assert any(('message', new_message) in msg.items() for msg in channel_messages) == True

def test_user_editing_not_channel_owner_or_author(clear_data, create_data):
    _, message_id, channel_id, new_message, _ = create_data

    # register new user, make them join channel
    register_data = requests.post(config.url + 'auth/register/v2', json={
                                                                           'email': 'boys@mycompany.com',
                                                                           'password': 'daboizindahood',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                          })

    # stores a token
    token3 = json.loads(register_data.text)['token']

    requests.post(config.url + 'channel/join/v2', json={
                                                          'token': token3,
                                                          'channel_id': channel_id,
                                                         })

    resp = requests.put(config.url + 'message/edit/v1', json={'token': token3,
                                                                'message_id': message_id,
                                                                'message': new_message
                                                                })
    assert resp.status_code == 403

def test_both_invalid_user_and_message_id(clear_data):
    invalid_message_id = 3248

    resp = requests.put(config.url + 'message/edit/v1', json={'token': 'invalid_token',
                                                                'message_id': invalid_message_id,
                                                                'message': 'oogabooga'
                                                                })
    assert resp.status_code == 403
