#channel_removeowner(token, channel_id, u_id):

import pytest

import json
import requests
from src import config

'''
InputError when any of:
    - channel_id does not refer to a valid channel[o]
    - u_id does not refer to a valid user[o]
    - u_id refers to a user who is not an owner of the channel[o]
    - u_id refers to a user who is currently the only owner of the channel[o]

    AccessError when:
    - channel_id is valid and the authorised user does not have owner permissions in the channel[o]

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
    token_1, user_1, _, user_2 = create_users

    channel_id = create_channel

    requests.post(config.url + 'channel/addowner/v1', json={
                                                                'token': token_1,
                                                                'channel_id': channel_id,
                                                                'u_id': user_2
                                                              })

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                              	  'token': token_1,
                                                                              	  'channel_id': channel_id,
                                                                              	  'u_id': user_2
                                                                            })
    assert remove_owner.status_code == 200

    channel_details = requests.get(config.url + 'channel/details/v2', params={
                                                                              'token': token_1,
                                                                              'channel_id': channel_id
                                                                            })
    owners = json.loads(channel_details.text)['owner_members']

    assert owners == [{ 'u_id': user_1,
                        'email': 'asd@gmail.com',
                        'name_first': 'lawrence',
                        'name_last': 'lee',
                        'handle_str': 'lawrencelee'}]

def test_invalid_channel_id(clear_data, create_users, create_channel):
    token_1, _, _, user_2 = create_users

    channel_id = create_channel

    requests.post(config.url + 'channel/addowner/v1', json={
                                                              	'token': token_1,
                                                              	'channel_id': channel_id,
                                                              	'u_id': user_2
                                                              })

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                              	  'token': token_1,
                                                                              	  'channel_id': 'not_channel_id',
                                                                              	  'u_id': user_2
                                                                            })
    assert remove_owner.status_code == 400

def test_removing_invalid_user(clear_data, create_users, create_channel):
    token_1, _, _, user_2 = create_users

    channel_id = create_channel

    requests.post(config.url + 'channel/addowner/v1', json={
                                                                'token': token_1,
                                                              	'channel_id': channel_id,
                                                              	'u_id': user_2
                                                              })

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                              	  'token': token_1,
                                                                              	  'channel_id': channel_id,
                                                                              	  'u_id': 'not_user_id'
                                                                            })
    assert remove_owner.status_code == 400

def test_remove_non_owner(clear_data, create_users, create_channel):
    token_1, _, _, user_2 = create_users

    channel_id = create_channel

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                              	  'token': token_1,
                                                                              	  'channel_id': channel_id,
                                                                              	  'u_id': user_2
                                                                            	})
    assert remove_owner.status_code == 400

def test_remove_only_owner(clear_data, create_users, create_channel):
    token_1, user_1, _, _ = create_users

    channel_id = create_channel

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                              'token': token_1,
                                                                              'channel_id': channel_id,
                                                                              'u_id': user_1
                                                                            })
    assert remove_owner.status_code == 400

def test_insufficient_permissions(clear_data, create_users, create_channel):
    _, user_1, token_2, _ = create_users

    channel_id = create_channel

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                              'token': token_2,
                                                                              'channel_id': channel_id,
                                                                              'u_id': user_1
                                                                            })
    assert remove_owner.status_code == 403

def test_invalid_token(clear_data, create_users, create_channel):
    _, _, _, user_2 = create_users

    channel_id = create_channel

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                              'token': 'token_1',
                                                                              'channel_id': channel_id,
                                                                              'u_id': user_2
                                                                            })
    assert remove_owner.status_code == 403

def test_remove_original_owner(clear_data, create_users, create_channel):
    token_1, user_1, token_2, user_2 = create_users

    channel_id = create_channel

    requests.post(config.url + 'channel/addowner/v1', json={
                                                              'token': token_1,
                                                              'channel_id': channel_id,
                                                              'u_id': user_2
                                                              })

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                              'token': token_2,
                                                                              'channel_id': channel_id,
                                                                              'u_id': user_1
                                                                            })
    assert remove_owner.status_code == 200

    channel_details = requests.get(config.url + 'channel/details/v2', params={
                                                                              'token': token_1,
                                                                              'channel_id': channel_id
                                                                            })
    owners = json.loads(channel_details.text)['owner_members']

    assert owners == [{ 'u_id': user_2,
                        'email': 'email2@gmail.com',
                        'name_first': 'christian',
                        'name_last': 'lam',
                        'handle_str': 'christianlam'}]

def test_channel_does_not_exist(clear_data, create_users, create_channel):
    token_1, _, _, user_2 = create_users

    resp = requests.post(config.url + 'channel/addowner/v1', json={
                                                              'token': token_1,
                                                              'channel_id': 2342,
                                                              'u_id': user_2
                                                              })
    assert resp.status_code == 400

def test_user_not_authorised(clear_data, create_users, create_channel):
  _, _, token_2, user_2 = create_users
  channel_id = create_channel

  resp = requests.post(config.url + 'channel/addowner/v1', json={
                                                              'token': token_2,
                                                              'channel_id': channel_id,
                                                              'u_id': user_2
                                                              })
  assert resp.status_code == 403
