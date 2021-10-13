import pytest

import json
import requests
from src import config
'''
InputError when:
      
    - any u_id in u_ids does not refer to a valid user
'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture 
#Pylint Error Idk How To Fix: dm_create_test.py:80:4: E0633: Attempting to unpack a non-sequence defined at line 17 (unpacking-non-sequence)
def create_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token
    token = json.loads(register_data.text)['token']

    # gets user_id
    user_id_0 = json.loads(register_data.text)['auth_user_id']

    # register user, log them in and get their user_id
    register_data_1 = requests.post(config.url + 'auth/register/v2', params={'email': 'HELLOOO@mycompany.com',
                                                                             'password': 'MYPPassword',
                                                                             'name_first': 'sfsdfFRSTName',
                                                                             'name_last': 'dssdLSTName'
                                                                             })

    # gets user_id
    user_id_1 = json.loads(register_data_1.text)['auth_user_id']

    # register user, log them in and get their user_id
    register_data_2 = requests.post(config.url + 'auth/register/v2', params={'email': 'HLOOO@mycompany.com',
                                                                             'password': 'MYPPassWOrd',
                                                                             'name_first': 'tyuuyFRSNme',
                                                                             'name_last': 'reqwLSName'
                                                                             })

    # gets user_id
    user_id_2 = json.loads(register_data_2.text)['auth_user_id']

    u_ids = [user_id_1, user_id_2]
    
    resp = requests.get(config.url + 'user/profile/v1', parameter = {'token': token,
                                                                     'u_id' : user_id_0
                                                                    })
    handle_0 = json.loads(resp.text)['user']['handle_str']

    resp = requests.get(config.url + 'user/profile/v1', parameter = {'token': token,
                                                                     'u_id' : user_id_1
                                                                    })
    handle_1 = json.loads(resp.text)['user']['handle_str']

    resp = requests.get(config.url + 'user/profile/v1', parameter = {'token': token,
                                                                     'u_id' : user_id_2
                                                                    })
    handle_2 = json.loads(resp.text)['user']['handle_str']

    name_handles = [handle_0, handle_1, handle_2]

    requests.post(config.url + 'dm/create/v1', params={'token': token,
                                                       'u_ids': u_ids
                                                       })
    return token, u_ids, name_handles


def test_simple_case(clear_data, create_data):
    token, u_ids, name_handles = create_data
    resp = requests.post(config.url + 'dm/create/v1', params={'token': token,
                                                              'u_ids': u_ids
                                                             })
    dm_id_test = json.loads(resp.text)['dm_id']
    assert type(dm_id_test) == int

    name = json.loads(resp.text)['name']
    assert name == name_handles

def test_invalid_user(clear_data, create_data):
    token, u_ids, _ = create_data
    invalid_u_id = 2342
    u_ids.append(invalid_u_id)

    resp = requests.post(config.url + 'dm/create/v1', params={'token': token,
                                                              'u_ids': u_ids
                                                              })

    assert resp.status_code == 400


def test_invalid_token(clear_data, create_data):
    _, u_ids, _ = create_data
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'heewllo@mycompany.com',
                                                                           'password': 'mypaweewssword',
                                                                           'name_first': 'Fiewwerstname',
                                                                           'name_last': 'Laewwewestname'
                                                                           })

    # stores a token
    invalid_token = json.loads(register_data.text)['token']

    resp = requests.post(config.url + 'dm/create/v1', params={'token': invalid_token,
                                                              'u_ids': u_ids
                                                              })

    assert resp.status_code == 403

def test_invalid_user_and_token(clear_data, create_data):
    _, u_ids, _ = create_data
    invalid_u_id = 2342
    u_ids.append(invalid_u_id)

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'heewllo@mycompany.com',
                                                                           'password': 'mypaweewssword',
                                                                           'name_first': 'Fiewwerstname',
                                                                           'name_last': 'Laewwewestname'
                                                                           })

    # stores a token
    invalid_token = json.loads(register_data.text)['token']

    resp = requests.post(config.url + 'dm/create/v1', params={'token': invalid_token,
                                                              'u_ids': u_ids
                                                              })

    assert resp.status_code == 403