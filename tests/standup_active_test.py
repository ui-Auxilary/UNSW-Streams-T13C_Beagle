import pytest

from src import config
import requests
import json

'''
For a given channel, return whether a standup is active in it, and what time the standup finishes. 
If no standup is active, then time_finish returns None.

InputError when:

    - channel_id does not refer to a valid channel

AccessError when:

    - channel_id is valid and the authorised user is not a member of the channel
        ie. Global owner has permissions, but is not in the channel

'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def register_user_data():
    register_data = requests.post(config.url + 'auth/register/v2', json={
        'email': 'joemama@gmail.com',
        'password': 'hijoeitsmama',
        'name_first': 'Joe',
        'name_last': 'Mama'
    })

    auth_user_id = json.loads(register_data.text)['auth_user_id']
    user_token = json.loads(register_data.text)['token']

    register_data_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'bobbyjones@gmail.com',
        'password': 'dillywillywobbo123',
        'name_first': 'Bobby',
        'name_last': 'Jones'
    })

    user_id_2 = json.loads(register_data_2.text)['auth_user_id']
    user_token_2 = json.loads(register_data_2.text)['token']

    return auth_user_id, user_token, user_id_2, user_token_2


@pytest.fixture
def user_and_channel_data(register_user_data):
    _, user_token, _, user_token_2 = register_user_data

    # create a public channel with global_owner
    channel_data = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token,
        'name': 'Public_owner_channel',
        'is_public': True
    })

    channel_id = json.loads(channel_data.text)['channel_id']

    # user_2 creates a public and private channel
    channel_data_2 = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token_2,
        'name': 'Public_user_channel',
        'is_public': True
    })

    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    # create a channel with that user
    channel_data_3 = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token_2,
        'name': 'Private_user_channel',
        'is_public': False
    })

    channel_id_3 = json.loads(channel_data_3.text)['channel_id']

    return user_token, user_token_2, channel_id, channel_id_2, channel_id_3


@pytest.fixture
def create_startup_data(clear_data, user_and_channel_data):
    auth_token, user_token_2, channel_1, channel_2, channel_3 = user_and_channel_data

    # auth_user creates a startup in channel_1
    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 60
    })

    # user_2 creates a startup in channel_2
    standup_start_data_2 = requests.post(config.url + 'standup/start/v1', json={
        'token': user_token_2,
        'channel_id': channel_2,
        'length': 120
    })

    # user_2 creates a startup in channel_3
    standup_start_data_3 = requests.post(config.url + 'standup/start/v1', json={
        'token': user_token_2,
        'channel_id': channel_3,
        'length': 300
    })

    # collect the time_finish for each startup
    time_finish_1 = json.loads(standup_start_data.text)['time_finish']
    time_finish_2 = json.loads(standup_start_data_2.text)['time_finish']
    time_finish_3 = json.loads(standup_start_data_3.text)['time_finish']

    return channel_1, time_finish_1, channel_2, time_finish_2, channel_3, time_finish_3

# ___SIMPLE TEST CASES - NO DEPENDANT FUNCTIONS___ #


def test_active_startup_public_channel(clear_data, register_user_data, create_startup_data):
    _, auth_token, _, _ = register_user_data
    channel_1, time_finish_1, _, _, _, _ = create_startup_data

    standup_active_data = requests.get(config.url + 'standup/active/v1', params={
        'token': auth_token,
        'channel_id': channel_1,
    })

    standup_is_active = json.loads(standup_active_data.text)['is_active']
    standup_duration = json.loads(standup_active_data.text)['time_finish']

    assert standup_is_active == True
    assert standup_duration == time_finish_1


def test_inactive_startup_public_channel(clear_data, user_and_channel_data):
    _, token_2, _, channel_2, _ = user_and_channel_data

    standup_active_data = requests.post(config.url + 'standup/start/v1', json={
        'token': token_2,
        'channel_id': channel_2
    })

    standup_is_active = json.loads(standup_active_data.text)['is_active']
    standup_duration = json.loads(standup_active_data.text)['time_finish']

    assert standup_is_active == False
    assert standup_duration == None


def test_active_startup_private_channel(clear_data, register_user_data, create_startup_data):
    _, _, _, user_token_2 = register_user_data
    _, _, _, _, channel_3, time_finish_3 = create_startup_data

    standup_active_data = requests.get(config.url + 'standup/active/v1', params={
        'token': user_token_2,
        'channel_id': channel_3,
    })

    standup_is_active = json.loads(standup_active_data.text)['is_active']
    standup_duration = json.loads(standup_active_data.text)['time_finish']

    assert standup_is_active == True
    assert standup_duration == time_finish_3


def test_inactive_startup_private_channel(clear_data, user_and_channel_data):
    _, token_2, _, _, channel_3 = user_and_channel_data

    standup_active_data = requests.post(config.url + 'standup/start/v1', json={
        'token': token_2,
        'channel_id': channel_3
    })

    standup_is_active = json.loads(standup_active_data.text)['is_active']
    standup_duration = json.loads(standup_active_data.text)['time_finish']

    assert standup_is_active == False
    assert standup_duration == None

# ___TEST VALID INPUT___ #


def test_invalid_channel_id(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    standup_active_data = requests.get(config.url + 'standup/active/v1', params={
        'token': auth_token,
        'channel_id': 123,
    })

    assert standup_active_data.status_code == 400

# ___TEST ACCESS PERMISSIONS ___ #


def test_valid_channel_user_not_channel_member(clear_data, user_and_channel_data):
    _, _, channel_1, _, _ = user_and_channel_data

    # register another user not in the channel
    register_data_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'user3@gmail.com',
        'password': 'user3password',
        'name_first': 'User',
        'name_last': '3'
    })

    user_token_3 = json.loads(register_data_3.text)['token']

    # user_3 tries to check for active standup in a valid channel
    standup_active_data = requests.get(config.url + 'standup/active/v1', params={
        'token': user_token_3,
        'channel_id': channel_1,
    })

    assert standup_active_data.status_code == 403
