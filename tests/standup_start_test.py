import pytest

from src import config
import requests
import json

'''
For a given channel, start the standup period whereby for the next "length" seconds if someone calls "standup/send" with a message,
it is buffered during the X second window then at the end of the X second window a message will be added to the message queue in 
the channel from the user who started the standup. "length" is an integer that denotes the number of seconds that the standup occurs
for.

InputError when:

    - channel_id does not refer to a valid channel
    - length is a negative integer
    - another active standup is running

AccessError when:

    - channel_id is valid and the authorised user is not a member of the channel
        ie. Global owner has permissions, but is not in the channel

What happens when:
    - id passed in is a dm_id, which is a valid channel id, but called in a DM

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


# ___SIMPLE TEST CASES - NO DEPENDANT FUNCTIONS___ #


def test_simple_case_public_channel(clear_data, user_and_channel_data):
    auth_token, _, channel_1, _, _ = user_and_channel_data

    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 10
    })

    standup_duration = json.loads(standup_start_data.text)['time_finish']

    assert type(standup_duration) == int


def test_simple_case_private_channel(clear_data, user_and_channel_data):
    _, token_2, _, _, channel_3 = user_and_channel_data

    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': token_2,
        'channel_id': channel_3,
        'length': 20
    })

    standup_duration = json.loads(standup_start_data.text)['time_finish']

    assert type(standup_duration) == int


def test_startup_duration_zero(clear_data, user_and_channel_data):
    _, token_2, _, channel_2, _ = user_and_channel_data

    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': token_2,
        'channel_id': channel_2,
        'length': 0
    })

    standup_duration = json.loads(standup_start_data.text)['time_finish']

    assert type(standup_duration) == int

# ___COMPLEX TEST CASES - DEPENDANT FUNCTIONS___ #


def test_non_owner_starts_channel_standup(clear_data, user_and_channel_data):
    auth_token, user_token_2, channel_1, _, _ = user_and_channel_data

    # user_2 joins channel_1 and starts a standup
    requests.post(config.url + 'channel/join/v2', json={
        'token': user_token_2,
        'channel_id': channel_1
    })

    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 60
    })

    time_finish = json.loads(standup_start_data.text)['time_finish']

    # check the standup is active
    standup_active_data = requests.get(config.url + 'standup/active/v1', params={
        'token': auth_token,
        'channel_id': channel_1,
    })

    standup_is_active = json.loads(standup_active_data.text)['is_active']
    standup_duration = json.loads(standup_active_data.text)['time_finish']

    assert standup_is_active == True
    assert standup_duration == time_finish


def test_start_multiple_standups_different_channels(clear_data, user_and_channel_data):
    auth_token, user_token_2, channel_1, channel_2, channel_3 = user_and_channel_data

    # user 1 starts a standup
    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 20
    })

    time_finish = json.loads(standup_start_data.text)['time_finish']

    # user 2 starts two standups
    standup_start_2_data = requests.post(config.url + 'standup/start/v1', json={
        'token': user_token_2,
        'channel_id': channel_2,
        'length': 60
    })

    time_finish_2 = json.loads(standup_start_2_data.text)['time_finish']

    standup_start_3_data = requests.post(config.url + 'standup/start/v1', json={
        'token': user_token_2,
        'channel_id': channel_3,
        'length': 300
    })

    time_finish_3 = json.loads(standup_start_3_data.text)['time_finish']

    # check the standups are active
    standup_active_data = requests.get(config.url + 'standup/active/v1', params={
        'token': auth_token,
        'channel_id': channel_1,
    })

    standup_is_active = json.loads(standup_active_data.text)['is_active']
    standup_duration = json.loads(standup_active_data.text)['time_finish']

    standup_active_data = requests.get(config.url + 'standup/active/v1', params={
        'token': user_token_2,
        'channel_id': channel_2,
    })

    standup_is_active_2 = json.loads(standup_active_data.text)['is_active']
    standup_duration_2 = json.loads(standup_active_data.text)['time_finish']

    standup_active_data = requests.get(config.url + 'standup/active/v1', params={
        'token': user_token_2,
        'channel_id': channel_3,
    })

    standup_is_active_3 = json.loads(standup_active_data.text)['is_active']
    standup_duration_3 = json.loads(standup_active_data.text)['time_finish']

    assert standup_is_active == True
    assert standup_duration == time_finish
    assert standup_is_active_2 == True
    assert standup_duration_2 == time_finish_2
    assert standup_is_active_3 == True
    assert standup_duration_3 == time_finish_3


def test_empty_startup(clear_data, user_and_channel_data):
    auth_token, _, channel_1, _, _ = user_and_channel_data

    # user 1 starts a standup
    requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 0
    })

    # get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
        'token': auth_token,
        'channel_id': channel_1,
        'start': 0
    })

    channel_messages = json.loads(channel_message_data.text)['messages']
    channel_end = json.loads(channel_message_data.text)['end']

    assert channel_messages[0]['message'] == ""
    assert channel_end == -1

# ___TEST VALID INPUT___ #


def test_invalid_channel_id(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': 123,
        'length': 60
    })

    assert standup_start_data.status_code == 400


def test_invalid_startup_duration(clear_data, user_and_channel_data):
    auth_token, _, channel_1, _, _ = user_and_channel_data

    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': -2
    })

    assert standup_start_data.status_code == 400


def test_existing_active_standup_in_channel(clear_data, user_and_channel_data):
    auth_token, token_2, channel_1, _, _ = user_and_channel_data

    # auth_user starts a valid standup
    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 120
    })

    assert standup_start_data.status_code == 200

    # user_2 joins channel_1
    requests.post(config.url + 'channel/join/v2', json={
        'token': token_2,
        'channel_id': channel_1
    })

    # user_2 attempts to start another standup in the same channel
    standup_start_2_data = requests.post(config.url + 'standup/start/v1', json={
        'token': token_2,
        'channel_id': channel_1,
        'length': 20
    })

    assert standup_start_2_data.status_code == 400

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

    # user_3 tries to start a standup in the channel
    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': user_token_3,
        'channel_id': channel_1,
        'length': 60
    })

    assert standup_start_data.status_code == 403

    # ___ TEST BOTH INPUT AND ACCESS ERRORS __ #


def test_user_not_channel_member_and_length_standup_invalid(clear_data, user_and_channel_data):
    _, _, channel_1, _, _ = user_and_channel_data

    # register another user not in the channel
    register_data_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'user3@gmail.com',
        'password': 'user3password',
        'name_first': 'User',
        'name_last': '3'
    })

    user_token_3 = json.loads(register_data_3.text)['token']

    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': user_token_3,
        'channel_id': channel_1,
        'length': -2
    })

    assert standup_start_data.status_code == 403


def test_existing_standup_in_channel_and_user_not_member(clear_data, user_and_channel_data):
    auth_token, _, channel_1, _, _ = user_and_channel_data

    # register another user not in the channel
    register_data_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'user3@gmail.com',
        'password': 'user3password',
        'name_first': 'User',
        'name_last': '3'
    })

    user_token_3 = json.loads(register_data_3.text)['token']

    # auth_user starts a valid standup
    standup_start_data = requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 60
    })

    assert standup_start_data.status_code == 200

    # user_3 attempts to start another standup in the same channel but isn't a channel member

    standup_start_2_data = requests.post(config.url + 'standup/start/v1', json={
        'token': user_token_3,
        'channel_id': channel_1,
        'length': 10
    })

    assert standup_start_2_data.status_code == 403
