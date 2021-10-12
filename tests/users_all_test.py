# users_all(token)

import pytest

import json
import requests
from src import config
'''
Returns a list of all users and their associated details.
    GET
    
Parameters:{ token }Return Type:{ users }

    N/A
'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token
    token = json.loads(register_data.text)['token']

    # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', params={'email': 'hello@hello.com',
                                                           'password': 'iuhuouiojk',
                                                           'name_first': 'samantha',
                                                           'name_last': 'tse'
                                                           })

    requests.post(config.url + 'auth/register/v2', params={'email': 'hdsfdfslo@mycompany.com',
                                                           'password': 'mypeqwewassword',
                                                           'name_first': 'lemon',
                                                           'name_last': 'pie'
                                                           })

    requests.post(config.url + 'auth/register/v2', params={'email': 'hdsfdfslo@gmail.com',
                                                           'password': 'mycvvcvcpassword',
                                                           'name_first': 'lebron',
                                                           'name_last': 'james'
                                                           })

    user_0 = {'u_id': 0, 'email': 'hello@mycompany.com', 'name_first': 'Firstname',
              'name_last': 'Lastname', 'handle_str': 'FirstnameLastname'}
    user_1 = {'u_id': 1, 'email': 'hello@hello.com', 'name_first': 'samantha',
              'name_last': 'tse', 'handle_str': 'samanthatse'}
    user_2 = {'u_id': 2, 'email': 'hdsfdfslo@mycompany.com',
              'name_first': 'lemon', 'name_last': 'pie', 'handle_str': 'lemonpie'}
    user_3 = {'u_id': 3, 'email': 'hdsfdfslo@gmail.com',
              'name_first': 'lebron', 'name_last': 'james', 'handle_str': 'lebronjames'}

    users_all = {'users': [user_0, user_1, user_2, user_3]}

    return token, users_all


def test_simple_case(clear_data, create_data):
    token, users_all, _ = create_data()

    resp = requests.put(config.url + 'users/all/v1', params={'token': token})

    assert resp == users_all
    assert resp['users'][0]['u_id'] == users_all['users'][0]['u_id']
    assert type(resp['users'][0]['u_id']) == int


def test_one_user(clear_data, create_data):
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token
    token = json.loads(register_data.text)['token']

    resp = requests.put(config.url + 'users/all/v1', params={'token': token})

    assert resp == {'users': [{'u_id': 0, 'email': 'hello@mycompany.com', 'name_first': 'Firstname',
                    'name_last': 'Lastname', 'handle_str': 'FirstnameLastname'}]}


def test_invalid_token(clear_data, create_data):
    token = str("s224fccs")

    resp = requests.put(config.url + 'users/all/v1', params={'token': token})

    assert resp == 403
