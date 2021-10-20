# channel_leave(token, channel_id)

import pytest

import json
import requests
from src import config

'''
InputError when:
    - channel_id does not refer to a valid channel

    AccessError when:
    - channel_id is valid and the authorised user is not a member of the channel
'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_users():
    register_user_1 = requests.post(config.url + 'auth/register/v2', json={
                                                                                'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })

    token_1 = json.loads(register_user_1.text)['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    register_user_2 = requests.post(config.url + 'auth/register/v2', json={
                                                                                'email': 'email2@gmail.com',
                                                                                'password': 'zxcvbnm',
                                                                                'name_first': 'christian',
                                                                                'name_last': 'lam'
                                                                              })

    token_2 = json.loads(register_user_2.text)['token']
    user_id_2 = json.loads(register_user_2.text)['auth_user_id']

    return token_1, user_id_1, token_2, user_id_2

@pytest.fixture
def create_channel(create_users):
    token_1, _, _, user_2 = create_users
    create_channel = requests.post(config.url + 'channels/create/v2', json={  
                                                                                'token': token_1,
                                                                                'name': 'channel',
                                                                                'is_public': True
                                                                              })
    channel_id = json.loads(create_channel.text)['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={  
                                                              'token': token_1,
                                                              'channel_id': channel_id,
                                                              'u_id': user_2
                                                            })
    return channel_id

def test_simple_case(clear_data, create_users, create_channel):
    token_1, user_1, token_2, _ = create_users

    channel_id = create_channel

    leave_channel = requests.post(config.url + 'channel/leave/v1', json={ 
                                                                              'token': token_2,
                                                                              'channel_id': channel_id,                                                                
                                                                            })
    
    assert leave_channel.status_code == 200
    channel_details = requests.get(config.url + 'channel/details/v2', params={ 
                                                                              'token': token_1,
                                                                              'channel_id': channel_id,                                                                
                                                                            })
    channel_members = json.loads(channel_details.text)['all_members']

    assert channel_members == [{ 'u_id': user_1,
                                 'email': 'asd@gmail.com',
                                 'name_first': 'lawrence',
                                 'name_last': 'lee',
                                 'handle_str': 'lawrencelee'
                                }]

def test_only_owner_leaves(clear_data, create_users, create_channel):
    token_1, _, token_2, user_2 = create_users

    channel_id = create_channel

    leave_channel = requests.post(config.url + 'channel/leave/v1', json={ 
                                                                          'token': token_1,
                                                                          'channel_id': channel_id,                                                                
                                                                        })
    
    assert leave_channel.status_code == 200
    
    channel_details = requests.get(config.url + 'channel/details/v2', params={ 
                                                                              'token': token_2,
                                                                              'channel_id': channel_id,                                                                
                                                                            })
    channel_members = json.loads(channel_details.text)['all_members']

    assert channel_members == [{ 'u_id': user_2,
                                 'email': 'email2@gmail.com',
                                 'name_first': 'christian',
                                 'name_last': 'lam',
                                 'handle_str': 'christianlam'
                                }]

def test_messages_remain(clear_data, create_users, create_channel):
    token_1, user_1, token_2, _ = create_users

    channel_id = create_channel

    create_message = requests.post(config.url + 'message/send/v1', json={ 
                                                                              'token': token_2,
                                                                              'channel_id': channel_id,
                                                                              'message': 'testing is quite fun'
                                                                              })
    message_id = json.loads(create_message.text)['message_id']

    leave_channel = requests.post(config.url + 'channel/leave/v1', json={ 
                                                                              'token': token_2,
                                                                              'channel_id': channel_id,                                                                
                                                                            })
    
    assert leave_channel.status_code == 200
    channel_details = requests.get(config.url + 'channel/details/v2', params={ 
                                                                              'token': token_1,
                                                                              'channel_id': channel_id,                                                                
                                                                            })
    channel_members = json.loads(channel_details.text)['all_members']

    assert channel_members == [{ 'u_id': user_1,
                                 'email': 'asd@gmail.com',
                                 'name_first': 'lawrence',
                                 'name_last': 'lee',
                                 'handle_str': 'lawrencelee'
                                }]

    channel_messages = requests.get(config.url + 'channel/messages/v2', params={ 
                                                                                  'token': token_1,
                                                                                  'channel_id': channel_id,
                                                                                  'start': 0
                                                                            })

    message_list = json.loads(channel_messages.text)['messages']

    assert any(('message_id', message_id) in messages.items() for messages in message_list) == True

def test_all_users_leave(clear_data, create_users, create_channel):
    token_1, user_1, token_2, _ = create_users

    channel_id = create_channel

    leave_channel = requests.post(config.url + 'channel/leave/v1', json={ 
                                                                              'token': token_2,
                                                                              'channel_id': channel_id                                                                
                                                                            })
    
    assert leave_channel.status_code == 200

    channel_details = requests.get(config.url + 'channel/details/v2', params={ 
                                                                              'token': token_1,
                                                                              'channel_id': channel_id                                                                
                                                                            })
    channel_members = json.loads(channel_details.text)['all_members']

    assert channel_members == [{ 'u_id': user_1,
                                 'email': 'asd@gmail.com',
                                 'name_first': 'lawrence',
                                 'name_last': 'lee',
                                 'handle_str': 'lawrencelee'
                                }]

    leave_channel = requests.post(config.url + 'channel/leave/v1', json={ 
                                                                              'token': token_1,
                                                                              'channel_id': channel_id                                                                
                                                                            })
    
    assert leave_channel.status_code == 200

    ## get the channel information to check it still exists
    channel_list_all = requests.get(config.url + 'channels/listall/v2', params={  
                                                                                'token': token_1
                                                                               })

    get_channels = json.loads(channel_list_all.text)['channels']

    assert get_channels == [{   
                                'channel_id': channel_id,
                                'name': 'channel'
                            }]

def test_invalid_channel(clear_data, create_users, create_channel):
    _, _, token_2, _ = create_users
    create_channel

    leave_channel = requests.post(config.url + 'channel/leave/v1', json={ 
                                                                          'token': token_2,
                                                                          'channel_id': 1221,                                                                
                                                                        })
    
    assert leave_channel.status_code == 400

def test_not_member_of_channel(clear_data, create_users, create_channel):
    _, _, token_2, _ = create_users
    channel_id = create_channel

    leave_channel = requests.post(config.url + 'channel/leave/v1', json={ 
                                                                              'token': token_2,
                                                                              'channel_id': channel_id                                                                
                                                                            })

    assert leave_channel.status_code == 200

    leave_channel = requests.post(config.url + 'channel/leave/v1', json={ 
                                                                              'token': token_2,
                                                                              'channel_id': channel_id
                                                                            })
    
    assert leave_channel.status_code == 403

def test_invalid_token(clear_data, create_channel):
    channel_id = create_channel

    leave_channel = requests.post(config.url + 'channel/leave/v1', json={ 
                                                                              'token': 'token_1',
                                                                              'channel_id': channel_id                                                                
                                                                            })

    assert leave_channel.status_code == 403
