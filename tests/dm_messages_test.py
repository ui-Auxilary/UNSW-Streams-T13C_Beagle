import pytest

from src import config
import requests
import json

'''
InputError when any of:
      
    dm_id does not refer to a valid DM
    start is greater than the total number of messages in the channel

AccessError when:

    dm_id is valid and the authorised user is not a member of the DM
      
'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token
    token = json.loads(register_data.text)['token']

    

    # register user, log them in and get their user_id
    register_data_1 = requests.post(config.url + 'auth/register/v2', json={'email': 'HELLOOO@mycompany.com',
                                                                           'password': 'MYPPassword',
                                                                           'name_first': 'FRSTName',
                                                                           'name_last': 'LSTName'
                                                                           })

    # gets user_id
    user_id_1 = json.loads(register_data_1.text)['auth_user_id']

    # register user, log them in and get their user_id
    register_data_2 = requests.post(config.url + 'auth/register/v2', json={'email': 'HLOOO@mycompany.com',
                                                                           'password': 'MYPPassWOrd',
                                                                           'name_first': 'FRSNme',
                                                                           'name_last': 'LSName'
                                                                           })
    # gets user_id
    user_id_2 = json.loads(register_data_2.text)['auth_user_id']


    u_ids = [user_id_1, user_id_2]

    dm_data = requests.post(config.url + 'dm/create/v1', json={
                                                                 'token': token,
                                                                 'u_ids': u_ids
                                                                })

    dm_id = json.loads(dm_data.text)['dm_id']

    return token, u_ids, dm_id

def test_simple_case(clear_data, create_data):
    token, _, dm_id = create_data
    start = 0

    for i in range (0, 60):
        requests.post(config.url + 'message/senddm/v1', json={'token': token,
                                                                        'dm_id': dm_id,
                                                                        'message': f"{i}"
                                                                        })

    dm_data = requests.get(config.url + 'dm/messages/v1', params={'token': token,
                                                                            'dm_id': dm_id,
                                                                            'start': start
                                                                            })


    dm_messages = json.loads(dm_data.text)['messages']
    dm_end = json.loads(dm_data.text)['end']

    assert len(dm_messages) == 49
    assert dm_end == 50

def test_non_zero_start(clear_data, create_data):
    token, _, dm_id = create_data
    start = 0

    for i in range (0, 50):
        requests.post(config.url + 'message/senddm/v1', json={'token': token,
                                                                        'dm_id': dm_id,
                                                                        'message': f"{i}"
                                                                        })

    dm_data = requests.get(config.url + 'dm/messages/v1', params={'token': token,
                                                                            'dm_id': dm_id,
                                                                            'start': start
                                                                            })


    dm_messages = json.loads(dm_data.text)['messages']
    dm_end = json.loads(dm_data.text)['end']

    assert len(dm_messages) == 49
    assert dm_end == -1

def test_no_messages(clear_data, create_data):
    token, _, dm_id = create_data
    start = 0

    dm_data = requests.get(config.url + 'dm/messages/v1', params={'token': token,
                                                                        'dm_id': dm_id,
                                                                        'start': start
                                                                        })

    dm_messages = json.loads(dm_data.text)['messages']
    dm_end = json.loads(dm_data.text)['end']

    assert len(dm_messages) == 0
    assert dm_messages == []
    assert dm_end == -1

def test_invalid_dm_id(clear_data, create_data):
    valid_token, _, _ = create_data

    invalid_dm_id = 329

    resp = requests.get(config.url + 'dm/messages/v1', params={'token': valid_token,
                                                               'dm_id': invalid_dm_id,
                                                               'start': 0
                                                               })

    assert resp.status_code == 400

def test_start_more_than_total_messages(clear_data, create_data):
    token, _, dm_id = create_data
    start = 300

    resp = requests.get(config.url + 'dm/messages/v1', params={'token': token,
                                                               'dm_id': dm_id,
                                                               'start': start
                                                               })

    assert resp.status_code == 400


def test_invalid_user(clear_data, create_data):
    _, _, dm_id = create_data

    resp = requests.get(config.url + 'dm/messages/v1', params={'token': 'sadasdasd',
                                                               'dm_id': dm_id,
                                                               'start': 0
                                                               })

    assert resp.status_code == 403


def test_end_more_than_total_messages_and_invalid_user(clear_data, create_data):
    _, _, dm_id = create_data
    start = 80

    result = requests.get(config.url + 'dm/messages/v1', params={'token': 'sadasd',
                                                                 'dm_id': dm_id,
                                                                 'start': start
                                                                 })

    assert result.status_code == 403


def test_no_messages_and_invalid_user(clear_data, create_data):
    _, _, dm_id = create_data

    result = requests.get(config.url + 'dm/messages/v1', params={'token': 'invalid_token',
                                                                 'dm_id': dm_id,
                                                                 'start': 0
                                                                 })

    assert result.status_code == 403


def test_invalid_dm_id_and_invalid_user(clear_data, create_data):
    invalid_dm_id = 9384

    resp = requests.get(config.url + 'dm/messages/v1', params={'token': 'invalid_token',
                                                               'dm_id': invalid_dm_id,
                                                               'start': 0
                                                               })

    assert resp.status_code == 403


def test_start_more_than_total_messages_and_invalid_user(clear_data, create_data):
    _, _, dm_id = create_data
    start = 300

    resp = requests.get(config.url + 'dm/messages/v1', params={'token': 'invalid_token',
                                                               'dm_id': dm_id,
                                                               'start': start
                                                               })

    assert resp.status_code == 403

def test_user_leave_dm_they_are_not_in(clear_data, create_data):
    _, _, dm_id = create_data
    start = 0

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'another@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token and user id
    auth_token_3 = json.loads(register_data.text)['token']

    dm_data = requests.get(config.url + 'dm/messages/v1', params={'token': auth_token_3,
                                                                            'dm_id': dm_id,
                                                                            'start': start
                                                                            })
    assert dm_data.status_code == 403
