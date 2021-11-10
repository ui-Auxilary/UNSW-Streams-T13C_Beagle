import pytest

import json
import requests
from src import config

'''
InputError when any of:      
    - both channel_id and dm_id are invalid
    - neither channel_id nor dm_id are -1        
    - og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    - length of message is more than 1000 characters
      
AccessError when:      
    - The pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised 
      user has not joined the channel or DM they are trying to share the message to


'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_users():
    register_user_1 = requests.post(config.url + 'auth/register/v2', json = { 'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })

    token_1 = json.loads(register_user_1.text)['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    register_user_2 = requests.post(config.url + 'auth/register/v2', json = { 'email': 'email2@gmail.com',
                                                                                'password': 'zxcvbnm',
                                                                                'name_first': 'christian',
                                                                                'name_last': 'lam'
                                                                              })

    token_2 = json.loads(register_user_2.text)['token']
    user_id_2 = json.loads(register_user_2.text)['auth_user_id']


    register_user_3 = requests.post(config.url + 'auth/register/v2', json = { 'email': 'email3@gmail.com',
                                                                                'password': 'something',
                                                                                'name_first': 'john',
                                                                                'name_last': 'doe'
                                                                              })

    token_3 = json.loads(register_user_3.text)['token']
    user_id_3 = json.loads(register_user_3.text)['auth_user_id']

    return token_1, user_id_1, token_2, user_id_2, token_3, user_id_3

@pytest.fixture
def create_channels(create_users):
    token_1, _, _, user_2, _, user_3 = create_users
    create_channel_1 = requests.post(config.url + 'channels/create/v2', json={
                                                                                'token': token_1,
                                                                                'name': 'channel1',
                                                                                'is_public': True
                                                                              })
    channel_id_1 = json.loads(create_channel_1.text)['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={
                                                              'token': token_1,
                                                              'channel_id': channel_id_1,
                                                              'u_id': user_2
                                                            })

    create_channel_2 = requests.post(config.url + 'channels/create/v2', json={
                                                                                'token': token_1,
                                                                                'name': 'channel2',
                                                                                'is_public': True
                                                                              })
    channel_id_2 = json.loads(create_channel_2.text)['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={
                                                              'token': token_1,
                                                              'channel_id': channel_id_2,
                                                              'u_id': user_3
                                                            })
    return channel_id_1, channel_id_2

@pytest.fixture
def create_dms(create_users):
    token_1, _, token_2, user_id_2, _, user_id_3 = create_users

    create_dm_1 = requests.post(config.url + 'dm/create/v1', json={'token': token_1,
                                                                   'u_ids': [user_id_2]
                                                                   })

    dm_id_1 = json.loads(create_dm_1.text)['dm_id']

    create_dm_2 = requests.post(config.url + 'dm/create/v1', json={'token': token_1,
                                                                   'u_ids': [user_id_3]
                                                                   })

    dm_id_2 = json.loads(create_dm_2.text)['dm_id']

    create_dm_3 = requests.post(config.url + 'dm/create/v1', json={'token': token_2,
                                                                   'u_ids': [user_id_3]
                                                                   })

    dm_id_3 = json.loads(create_dm_3.text)['dm_id']

    return dm_id_1, dm_id_2, dm_id_3

def test_share_channel_to_dm(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': message_id,
                                                                  'message': '',
                                                                  'channel_id': -1,
                                                                  'dm_id': dm_id
                                                                })
    
    assert share.status_code == 200
    
    share_msg_id = json.loads(share.text)['shared_message_id']
    
    dm_message_data = requests.get(config.url + 'dm/messages/v1', params={
                                                               'token': token_1,
                                                               'dm_id': dm_id,
                                                               'start': 0
                                                               })

    message_list = json.loads(dm_message_data.text)['messages']

    assert share_msg_id != message_id
    assert any(('message', message) in msg.items() for msg in message_list)
    
def test_share_dm_to_channel(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/senddm/v1', json={
                                                                          'token': token_1,
                                                                          'dm_id': dm_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': message_id,
                                                                  'message': '',
                                                                  'channel_id': channel_id,
                                                                  'dm_id': -1
                                                                })
    
    assert share.status_code == 200
    
    share_msg_id = json.loads(share.text)['shared_message_id']

    message_data = requests.get(config.url + 'channel/messages/v2', params={
        'token': token_1,
        'channel_id': channel_id,
        'start': 0
    })

    message_list = json.loads(message_data.text)['messages']

    assert any(('message', message) in msg.items() for msg in message_list)
    
def test_share_channel_to_channel(clear_data, create_users, create_channels):
    token_1, _, _, _, _, _ = create_users
    channel_id_1, channel_id_2 = create_channels
    message = "imagine"
    new_message = "hey"

    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id_1,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': message_id,
                                                                  'message': new_message,
                                                                  'channel_id': channel_id_2,
                                                                  'dm_id': -1
                                                                })
    
    assert share.status_code == 200
    
    share_msg_id = json.loads(share.text)['shared_message_id']
    
    message_data = requests.get(config.url + 'channel/messages/v2', params={
        'token': token_1,
        'channel_id': channel_id_2,
        'start': 0
    })

    message_list = json.loads(message_data.text)['messages']
    
    assert any(('message', message + new_message) in msg.items() for msg in message_list)


def test_share_dm_to_dm(clear_data, create_users, create_dms):
    token_1, _, _, _, _, _ = create_users
    dm_id, _, _ = create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/senddm/v1', json={
                                                                          'token': token_1,
                                                                          'dm_id': dm_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': message_id,
                                                                  'message': '',
                                                                  'channel_id': -1,
                                                                  'dm_id': dm_id
                                                                })
    
    assert share.status_code == 200
    
    share_msg_id = json.loads(share.text)['shared_message_id']
    dm_message_data = requests.get(config.url + 'dm/messages/v1', params={
                                                               'token': token_1,
                                                               'dm_id': dm_id,
                                                               'start': 0
                                                               })

    message_list = json.loads(dm_message_data.text)['messages']

    assert share_msg_id != message_id
    assert any(('message', message) in msg.items() for msg in message_list)
    
def test_share_with_optional_msg(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = 'imagine'
    optional_msg = 'this is so cool'
    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': message_id,
                                                                  'message': optional_msg,
                                                                  'channel_id': -1,
                                                                  'dm_id': dm_id
                                                                })
    
    assert share.status_code == 200
    
    share_msg_id = json.loads(share.text)['shared_message_id']
    dm_message_data = requests.get(config.url + 'dm/messages/v1', params={
                                                               'token': token_1,
                                                               'dm_id': dm_id,
                                                               'start': 0
                                                               })

    message_list = json.loads(dm_message_data.text)['messages']

    assert share_msg_id != message_id
    assert any(('message', message + optional_msg) in msg.items() for msg in message_list)


# ___TEST INVALID INPUT___ #


def test_invalid_dm_and_channel(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': message_id,
                                                                  'message': '',
                                                                  'channel_id': 'channel',
                                                                  'dm_id': 'dm'
                                                                })
    
    assert share.status_code == 400
    
def test_neither_id_negative_one(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': message_id,
                                                                  'message': '',
                                                                  'channel_id': channel_id,
                                                                  'dm_id': dm_id
                                                                })
    
    assert share.status_code == 400
    
def test_both_negative_one(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': message_id,
                                                                  'message': '',
                                                                  'channel_id': -1,
                                                                  'dm_id': -1
                                                                })
    
    assert share.status_code == 400
    
def test_invalid_og_id(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,
                                                                          'message': message
                                                                        })
    
    json.loads(send_message.text)
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': 'message_id',
                                                                  'message': '',
                                                                  'channel_id': -1,
                                                                  'dm_id': dm_id
                                                                })
    
    assert share.status_code == 400
    
def test_invalid_message_length(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    opt_msg = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam nec sagittis sem, id aliquet est. Maecenas dignissim gravida enim at vehicula,\
                Vestibulum non ullamcorper ante. Integer pellentesque placerat urna et mollis. Donec ornare, nisl id fringilla suscipit, diam diam viverra nibh, \
                aliquet lacinia diam ipsum ac nunc. Suspendisse aliquet dolor pretium mi ornare, non egestas purus tempus. Proin ut eros venenatis, vestibulum nunc at, pretium orci,\
                Quisque convallis purus feugiat nisl fermentum euismod. Nunc ornare ultricies leo sit amet vehicula. Sed at sem nibh. Integer pellentesque ac libero ac semper.\
                Vestibulum laoreet blandit felis, ac mattis erat dignissim vitae. In ut quam at urna placerat ultricies. Pellentesque nibh velit, interdum sit amet risus sed,\
                mollis sagittis nulla. Suspendisse leo justo, congue a varius vitae, venenatis at ipsum. Nunc porttitor velit et porttitor pretium. Duis in lacus et lorem feugiat,\
                cursus pulvinar non augue. Morbi non est nibh. Sed non tincidunt leo, non condimentum felis. Nunc mattis rutrum fringilla. Morbi ultricies ornare felis, at vulputate risus\
                mollis sed. Sed a dapibus neque, Etiam blandit egestas erat eget rutrum. Nunc scelerisque nulla est, vehicula lacinia leo dapibus quis. Duis eleifend diam ipsum, vitae \
                pretium lorem euismod sed. Duis vel'

    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_1,
                                                                  'og_message_id': message_id,
                                                                  'message': opt_msg,
                                                                  'channel_id': -1,
                                                                  'dm_id': dm_id
                                                                })
    
    assert share.status_code == 400
    

# ___TEST ACCESS PERMISSIONS ___ #


def test_invalid_token(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': 'token_1',
                                                                  'og_message_id': message_id,
                                                                  'message': '',
                                                                  'channel_id': -1,
                                                                  'dm_id': dm_id
                                                                })
    
    assert share.status_code == 403
    
def test_unauthorized_share(clear_data, create_users, create_channels, create_dms):
    token_1, _, _, _, token_3, _ = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = "imagine"

    send_message = requests.post(config.url + 'message/send/v1', json={
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,
                                                                          'message': message
                                                                        })
    
    message_id = json.loads(send_message.text)['message_id']
    
    share = requests.post(config.url + 'message/share/v1', json={
                                                                  'token': token_3,
                                                                  'og_message_id': message_id,
                                                                  'message': '',
                                                                  'channel_id': -1,
                                                                  'dm_id': dm_id
                                                                })
    
    assert share.status_code == 403