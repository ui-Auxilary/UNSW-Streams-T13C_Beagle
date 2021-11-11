import pytest

from src import config
import requests
import json
from datetime import timezone, datetime

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

    register_data_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'bobbybobby@gmail.com',
        'password': 'dillywillywobbo123',
        'name_first': 'Bob',
        'name_last': 'Jon'
    })

    user_id_3 = json.loads(register_data_3.text)['auth_user_id']
    user_token_3 = json.loads(register_data_3.text)['token']

    return auth_user_id, user_token, user_id_2, user_token_2, user_id_3, user_token_3


@pytest.fixture
def user_and_channel_data(register_user_data):
    _, user_token, user_id_2, user_token_2, _, user_token_3 = register_user_data

    # create a public channel with global_owner
    channel_data = requests.post(config.url + 'dm/create/v1', json={
        'token': user_token,
        'u_ids': [user_id_2]
    })

    dm_id = json.loads(channel_data.text)['dm_id']

    # create a channel with that user
    channel_data_2 = requests.post(config.url + 'dm/create/v1', json={
        'token': user_token_3,
        'u_ids': [user_id_2]
    })

    dm_id_2 = json.loads(channel_data_2.text)['dm_id']

    return user_token, user_token_2, dm_id, dm_id_2

def test_message_sendlater_simple(clear_data, user_and_channel_data):
    user_token, _, dm_id, _ = user_and_channel_data

    # get current time
    dt = datetime.now(timezone.utc)
    time_sent = int(dt.timestamp()) + 2

    message_data = requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': user_token,
        'dm_id': dm_id,
        'message': 'Hello this is a message',
        'time_sent': time_sent
    })

    message_id = json.loads(message_data.text)['message_id']
    assert type(message_id) == int

def test_message_sendlater_to_past(clear_data, user_and_channel_data):
    user_token, _, channel_id, _= user_and_channel_data

    # get current time
    dt = datetime.now(timezone.utc)
    time_sent = int(dt.timestamp()) - 5

    message_data = requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': user_token,
        'dm_id': channel_id,
        'message': 'Hello this is a message',
        'time_sent': time_sent
    })

    assert message_data.status_code == 400

def test_message_sendlater_to_invalid_channel(clear_data, user_and_channel_data):
    user_token, _, _, _ = user_and_channel_data

    # get current time
    dt = datetime.now(timezone.utc)
    time_sent = int(dt.timestamp()) + 5

    ## NOTE: WHITEBOX TEST AS WE ARE ASSUMING CHANNEL 5000 DOES NOT EXIST
    message_data = requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': user_token,
        'dm_id': 5000,
        'message': 'Hello this is a message',
        'time_sent': time_sent
    })

    assert message_data.status_code == 400

def test_message_sendlater_too_long(clear_data, user_and_channel_data):
    user_token, _, channel_id, _ = user_and_channel_data

    # get current time
    dt = datetime.now(timezone.utc)
    time_sent = int(dt.timestamp()) + 2

    message_data = requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': user_token,
        'dm_id': channel_id,
        'message': 'jdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdjafkjdflsajfkdasfkdj',
        'time_sent': time_sent
    })

    assert message_data.status_code == 400

def test_message_sendlater_user_not_in_channel(clear_data, user_and_channel_data):
    user_token, _, _, channel_id_3 = user_and_channel_data

    # get current time
    dt = datetime.now(timezone.utc)
    time_sent = int(dt.timestamp()) + 2

    message_data = requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': user_token,
        'dm_id': channel_id_3,
        'message': 'Hello this is a message',
        'time_sent': time_sent
    })

    assert message_data.status_code == 403
