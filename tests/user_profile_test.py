import pytest

import json
import requests
from src import config

'''
For a valid user, returns information about their user_id, email, first name, last name, and handle

InputError when:

    - u_id does not refer to a valid user
'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_data(clear_data):
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'hello@mycompany.com',
                                                                         'password': 'mypassword',
                                                                         'name_first': 'Firstname',
                                                                         'name_last': 'Lastname'
                                                                         })
    # gets user_id
    print(register_data.text)
    user_id = json.loads(register_data.text)['auth_user_id']

    # stores a token
    token = json.loads(register_data.text)['token']

    user_0 = {'u_id': user_id, 'email': 'hello@mycompany.com', 'name_first': 'Firstname',
              'name_last': 'Lastname', 'handle_str': 'firstnamelastname'}

    return token, user_0, user_id


def test_simple_case(clear_data, create_data):
    token, user_0, user_id = create_data

    resp = requests.get(config.url + 'user/profile/v1',
                        params={'token': token, 'u_id': user_id})

    assert json.loads(resp.text)['user'] == user_0


def test_invalid_u_id(clear_data, create_data):
    token, _, _ = create_data
    invalid_user_id = 1342

    resp = requests.get(config.url + 'user/profile/v1',
                        params={'token': token, 'u_id': invalid_user_id})

    assert resp.status_code == 400


def test_invalid_token(clear_data, create_data):
    _, _, user_id = create_data
    invalid_token = str("fjsldsdf")

    resp = requests.get(config.url + 'user/profile/v1',
                        params={'token': invalid_token, 'u_id': user_id})

    assert resp.status_code == 403


def test_invalid_both_token_and_u_id(clear_data, create_data):
    invalid_token = str("fjsldsdf")
    invalid_user_id = 1342

    resp = requests.get(config.url + 'user/profile/v1',
                        params={'token': invalid_token, 'u_id': invalid_user_id})

    assert resp.status_code == 403
