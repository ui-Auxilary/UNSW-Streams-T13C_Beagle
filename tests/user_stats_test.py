import pytest

import json
import requests
from src import config



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

def test_no_channels_or_dms(clear_data, create_users):
    token_1, _, _, _, _, _ = create_users

    stats = requests.get(config.url + 'user/stats/v1', params={ 'token': token_1})

    assert stats.status_code == 200

    user_stats = json.loads(stats.text)
    channels_joined = json.loads(stats.text)['channels_joined']
    dms_joined = json.loads(stats.text)['dms_joined']
    messages = json.loads(stats.text)['messages_sent']
    rate = json.loads(stats.text)['involvement_rate']

    assert user_stats == {
                          'channels_joined': channels_joined,
                          'dms_joined': dms_joined, 
                          'messages_sent': messages, 
                          'involvement_rate': rate
                        }

def test_join_single_channel(clear_data, create_users, create_channels):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    message = "imagine"

    requests.post(config.url + 'message/send/v1', json={
                                                          'token': token_1,
                                                          'channel_id': channel_id,
                                                          'message': message
                                                        })

    stats = requests.get(config.url + 'user/stats/v1', params={ 
                                                                  'token': token_1
                                                                })

    assert stats.status_code == 200

    user_stats = json.loads(stats.text)
    channels_joined = json.loads(stats.text)['channels_joined']
    dms_joined = json.loads(stats.text)['dms_joined']
    messages = json.loads(stats.text)['messages_sent']
    rate = json.loads(stats.text)['involvement_rate']

    assert user_stats == {
                          'channels_joined': channels_joined,
                          'dms_joined': dms_joined, 
                          'messages_sent': messages, 
                          'involvement_rate': rate
                        }

def test_channel_and_dm(clear_data, create_users, create_channels, create_dms):
    token, _, _, _, _, _, = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = "imagine"

    requests.post(config.url + 'message/send/v1', json={
                                                          'token': token,
                                                          'channel_id': channel_id,
                                                          'message': message
                                                        })

    requests.post(config.url + 'message/senddm/v1', json={  
                                                              'token': token,
                                                              'dm_id': dm_id,
                                                              'message': message
                                                            })

    stats = requests.get(config.url + 'user/stats/v1', params={ 
                                                                  'token': token
                                                                })

    assert stats.status_code == 200

    user_stats = json.loads(stats.text)
    channels_joined = json.loads(stats.text)['channels_joined']
    dms_joined = json.loads(stats.text)['dms_joined']
    messages = json.loads(stats.text)['messages_sent']
    rate = json.loads(stats.text)['involvement_rate']

    assert user_stats == {
                              'channels_joined': channels_joined,
                              'dms_joined': dms_joined, 
                              'messages_sent': messages, 
                              'involvement_rate': rate
                        }

def test_multiple_channels_and_dms(clear_data, create_users, create_channels, create_dms):
    token_1, _, token_2, _, token_3, _, = create_users
    channel_id_1, channel_id_2 = create_channels
    dm_id_1, dm_id_2, _ = create_dms
    message_1 = "imagine"
    message_2 = "imagine dragon"
    message_3 = "deez peanuts"
    message_4 = "cringe"

    requests.post(config.url + 'message/send/v1', json={
                                                          'token': token_1,
                                                          'channel_id': channel_id_1,
                                                          'message': message_1
                                                        })

    requests.post(config.url + 'message/send/v1', json={
                                                          'token': token_1,
                                                          'channel_id': channel_id_2,
                                                          'message': message_3
                                                        })

    requests.post(config.url + 'message/senddm/v1', json={  
                                                              'token': token_2,
                                                              'dm_id': dm_id_1,
                                                              'message': message_2
                                                            })

    requests.post(config.url + 'message/senddm/v1', json={
                                                              'token': token_3,
                                                              'dm_id': dm_id_2,
                                                              'message': message_4
                                                            })

    stats = requests.get(config.url + 'user/stats/v1', params={ 
                                                                  'token': token_1
                                                                })

    assert stats.status_code == 200

    user_stats = json.loads(stats.text)
    channels_joined = json.loads(stats.text)['channels_joined']
    dms_joined = json.loads(stats.text)['dms_joined']
    messages = json.loads(stats.text)['messages_sent']
    rate = json.loads(stats.text)['involvement_rate']

    assert user_stats == {
                              'channels_joined': channels_joined,
                              'dms_joined': dms_joined, 
                              'messages_sent': messages, 
                              'involvement_rate': rate
                        }
    
    stats = requests.get(config.url + 'user/stats/v1', params={ 
                                                                  'token': token_2
                                                                })

    assert stats.status_code == 200

    user_stats = json.loads(stats.text)
    channels_joined = json.loads(stats.text)['channels_joined']
    dms_joined = json.loads(stats.text)['dms_joined']
    messages = json.loads(stats.text)['messages_sent']
    rate = json.loads(stats.text)['involvement_rate']

    assert user_stats == {
                              'channels_joined': channels_joined,
                              'dms_joined': dms_joined, 
                              'messages_sent': messages, 
                              'involvement_rate': rate
                        }
    
    stats = requests.get(config.url + 'user/stats/v1', params={ 
                                                                  'token': token_3
                                                                })

    assert stats.status_code == 200

    user_stats = json.loads(stats.text)
    channels_joined = json.loads(stats.text)['channels_joined']
    dms_joined = json.loads(stats.text)['dms_joined']
    messages = json.loads(stats.text)['messages_sent']
    rate = json.loads(stats.text)['involvement_rate']

    assert user_stats == {
                              'channels_joined': channels_joined,
                              'dms_joined': dms_joined, 
                              'messages_sent': messages, 
                              'involvement_rate': rate
                        }

def test_invalid_token(clear_data, create_users, create_channels):
    token_1, _, _, _, _, _ = create_users
    channel_id, _ = create_channels
    message = "imagine"

    requests.post(config.url + 'message/send/v1', json={
                                                          'token': token_1,
                                                          'channel_id': channel_id,
                                                          'message': message
                                                        })

    stats = requests.get(config.url + 'user/stats/v1', params={ 
                                                                  'token': 'token_1'
                                                                })

    assert stats.status_code == 403