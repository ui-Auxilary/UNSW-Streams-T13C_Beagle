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
def create_data(clear_data):
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token
    token = json.loads(register_data.text)['token']
    user_id_0 = json.loads(register_data.text)['auth_user_id'] 

    # register user, log them in and get their user_id
    register_user_1 = requests.post(config.url + 'auth/register/v2', json={'email': 'hello@hello.com',
                                                           'password': 'iuhuouiojk',
                                                           'name_first': 'samantha',
                                                           'name_last': 'tse'
                                                           })
    
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']    

    register_user_2 = requests.post(config.url + 'auth/register/v2', json={'email': 'hdsfdfslo@mycompany.com',
                                                           'password': 'mypeqwewassword',
                                                           'name_first': 'lemon',
                                                           'name_last': 'pie'
                                                           })

    user_id_2 = json.loads(register_user_2.text)['auth_user_id'] 

    register_user_3 = requests.post(config.url + 'auth/register/v2', json={'email': 'hdsfdfslo@gmail.com',
                                                           'password': 'mycvvcvcpassword',
                                                           'name_first': 'lebron',
                                                           'name_last': 'james'
                                                           })

    user_id_3 = json.loads(register_user_3.text)['auth_user_id'] 

    user_0 = {'u_id': user_id_0, 'email': 'hello@mycompany.com', 'name_first': 'Firstname',
              'name_last': 'Lastname', 'handle_str': 'firstnamelastname'}
    user_1 = {'u_id': user_id_1, 'email': 'hello@hello.com', 'name_first': 'samantha',
              'name_last': 'tse', 'handle_str': 'samanthatse'}
    user_2 = {'u_id': user_id_2, 'email': 'hdsfdfslo@mycompany.com',
              'name_first': 'lemon', 'name_last': 'pie', 'handle_str': 'lemonpie'}
    user_3 = {'u_id': user_id_3, 'email': 'hdsfdfslo@gmail.com',
              'name_first': 'lebron', 'name_last': 'james', 'handle_str': 'lebronjames'}

    users_all = {'users': [user_0, user_1, user_2, user_3]}

    return token, users_all


def test_simple_case(clear_data, create_data):
    token, users_all = create_data

    resp = requests.get(config.url + 'users/all/v1', params={'token': token})
    resp = json.loads(resp.text)

    assert resp == users_all
    assert resp['users'][0]['u_id'] == users_all['users'][0]['u_id']


def test_one_user(clear_data):
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token
    token = json.loads(register_data.text)['token']
    user_id = json.loads(register_data.text)['auth_user_id']

    resp = requests.get(config.url + 'users/all/v1', params={'token': token})
    resp = json.loads(resp.text)

    assert resp == {'users': [{'u_id': user_id, 'email': 'hello@mycompany.com', 'name_first': 'Firstname',
                    'name_last': 'Lastname', 'handle_str': 'firstnamelastname'}]}


def test_invalid_token(clear_data, create_data):
    token = 's224fccs'

    resp = requests.get(config.url + 'users/all/v1', params={'token': token})

    assert resp.status_code == 403
