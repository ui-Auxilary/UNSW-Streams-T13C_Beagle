import pytest

from src import config
import requests
import json


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

    token = json.loads(register_data.text)['token']

    requests.post(config.url + 'auth/logout/v1', json={'token': token})

    ## User logs in twice, to get two valid token sessions
    login_1_data = requests.post(config.url + 'auth/login/v2', json={'email': 'hello@mycompany.com',
                                                                       'password': 'mypassword'
                                                                       })

    # stores another token
    token_1 = json.loads(login_1_data.text)['token']

    login_2_data = requests.post(config.url + 'auth/login/v2', json={'email': 'hello@mycompany.com',
                                                                       'password': 'mypassword'
                                                                       })

    # stores another token
    token_2 = json.loads(login_2_data.text)['token']

    # create a channel with that user
    requests.post(config.url + 'channels/create/v2', json={'token': token_1,
                                                             'name': 'channel_1',
                                                             'is_public': True
                                                             })

    return token_1, token_2


def test_simple_case(clear_data, create_data):
    token, _ = create_data

    requests.post(config.url + 'auth/logout/v1', json={'token': token})

    channels_list = requests.get(config.url + 'channels/list/v2', params={'token': token})

    channels_list_data = json.loads(channels_list.text)['code']

    assert channels_list_data == 403


def test_double_logout(clear_data, create_data):
    token1, _ = create_data
    requests.post(config.url + 'auth/logout/v1', json={'token': token1})

    logout = requests.post(config.url + 'auth/logout/v1', json={'token': token1})

    assert logout.status_code == 403


def test_double_login_one_logout(clear_data, create_data):
    token1, token2 = create_data

    logout1 = requests.post(config.url + 'auth/logout/v1', json={'token': token1 })

    assert logout1.status_code == 200

    channels_list = requests.get(config.url + 'channels/list/v2', params={'token': token2 })

    assert channels_list.status_code == 200

    channels_list_data = json.loads(channels_list.text)['channels']

    assert channels_list_data == [{'channel_id': 1, 'name': 'channel_1'}]

    assert logout1.status_code == 200


def test_invalid_token(clear_data):
    invalid_token = 432
    logout = requests.post(config.url + 'auth/logout/v1', json={'token': invalid_token})

    assert logout.status_code == 403
