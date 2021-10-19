import pytest

import json
import requests
from src import config
'''
InputError when:

    - any u_id in u_ids does not refer to a valid user
    - add test case for no_users
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

    # gets user_id
    user_id_0 = json.loads(register_data.text)['auth_user_id']

    # register user, log them in and get their user_id
    register_data_1 = requests.post(config.url + 'auth/register/v2', json={'email': 'HELLOOO@mycompany.com',
                                                                             'password': 'MYPPassword',
                                                                             'name_first': 'sfsdfFRSTName',
                                                                             'name_last': 'dssdLSTName'
                                                                             })

    # gets user_id
    user_id_1 = json.loads(register_data_1.text)['auth_user_id']

    # register user, log them in and get their user_id
    register_data_2 = requests.post(config.url + 'auth/register/v2', json={'email': 'HLOOO@mycompany.com',
                                                                             'password': 'MYPPassWOrd',
                                                                             'name_first': 'tyuuyFRSNme',
                                                                             'name_last': 'reqwLSName'
                                                                             })

    # gets user_id
    user_id_2 = json.loads(register_data_2.text)['auth_user_id']

    u_ids = [user_id_1, user_id_2]

    user_profile_1 = requests.get(config.url + 'user/profile/v1', params = {'token': token,
                                                                     'u_id' : user_id_0
                                                                    })

    handle_0 = json.loads(user_profile_1.text)['user']['handle_str']

    user_profile_2 = requests.get(config.url + 'user/profile/v1', params = {'token': token,
                                                                     'u_id' : user_id_1
                                                                    })
    handle_1 = json.loads(user_profile_2.text)['user']['handle_str']

    user_profile_3 = requests.get(config.url + 'user/profile/v1', params = {'token': token,
                                                                     'u_id' : user_id_2
                                                                    })

    handle_2 = json.loads(user_profile_3.text)['user']['handle_str']

    name_handles = [handle_0, handle_1, handle_2]

    dm_create_data  = requests.post(config.url + 'dm/create/v1', json={
                                                                         'token': token,
                                                                         'u_ids': u_ids
                                                                        })

    dm_id = json.loads(dm_create_data.text)['dm_id']

    return token, user_id_0, u_ids, name_handles, dm_id


def test_simple_case(clear_data, create_data):
    token, _, _, name_handles, dm_id = create_data

    assert type(dm_id) == int

    dm_details_data = requests.get(config.url + 'dm/details/v1', params={'token': token,
                                                                         'dm_id': dm_id
                                                                        })

    name = json.loads(dm_details_data.text)['name']

    assert name == ', '.join(name_handles)

def test_create_no_uids(clear_data, create_data):
    token, user_id_0, _, _, _ = create_data

    dm_create_data = requests.post(config.url + 'dm/create/v1', json={
                                                                         'token': token,
                                                                         'u_ids': []
                                                                        })
    assert dm_create_data.status_code == 200
    dm_id = json.loads(dm_create_data.text)['dm_id']

    dm_details_data = requests.get(config.url + 'dm/details/v1', params={'token': token,
                                                                         'dm_id': dm_id
                                                                        })

    assert dm_details_data.status_code == 200

    dm_details_data = requests.get(config.url + 'dm/details/v1', params={'token': token,
                                                                         'dm_id': dm_id
                                                                        })

    name = json.loads(dm_details_data.text)['name']

    user_profile_1 = requests.get(config.url + 'user/profile/v1', params = {'token': token,
                                                                     'u_id' : user_id_0
                                                                    })

    handle_0 = json.loads(user_profile_1.text)['user']['handle_str']

    assert name == handle_0

def test_create_dm_one_uid(clear_data, create_data):
    token, user_id_0, u_ids, _, _ = create_data

    user_id_1 = u_ids[0]

    dm_create_data = requests.post(config.url + 'dm/create/v1', json={
                                                                         'token': token,
                                                                         'u_ids': [user_id_1]
                                                                        })
    assert dm_create_data.status_code == 200
    dm_id = json.loads(dm_create_data.text)['dm_id']

    dm_details_data = requests.get(config.url + 'dm/details/v1', params={'token': token,
                                                                         'dm_id': dm_id
                                                                        })

    assert dm_details_data.status_code == 200

    dm_details_data = requests.get(config.url + 'dm/details/v1', params={'token': token,
                                                                         'dm_id': dm_id
                                                                        }) 

    name = json.loads(dm_details_data.text)['name']

    user_profile_0 = requests.get(config.url + 'user/profile/v1', params = {'token': token,
                                                                     'u_id' : user_id_0
                                                                    })

    handle_0 = json.loads(user_profile_0.text)['user']['handle_str']

    user_profile_1 = requests.get(config.url + 'user/profile/v1', params = {'token': token,
                                                                     'u_id' : user_id_1
                                                                    })

    handle_1 = json.loads(user_profile_1.text)['user']['handle_str']

    assert name == ', '.join([handle_0,handle_1])

def test_invalid_user(clear_data, create_data):
    token, _, u_ids, _, _ = create_data
    invalid_u_id = 2342
    u_ids.append(invalid_u_id)

    resp = requests.post(config.url + 'dm/create/v1', json={'token': token,
                                                              'u_ids': u_ids
                                                              })

    assert resp.status_code == 400


def test_invalid_token(clear_data, create_data):
    _, _, u_ids, _, _= create_data

    resp = requests.post(config.url + 'dm/create/v1', json={'token': 'Iliketrains',
                                                              'u_ids': u_ids
                                                              })

    assert resp.status_code == 403

def test_invalid_user_and_token(clear_data, create_data):
    _, _, u_ids, _, _ = create_data
    invalid_u_id = 2342
    u_ids.append(invalid_u_id)

    resp = requests.post(config.url + 'dm/create/v1', json={'token': 'Yothisatoken',
                                                              'u_ids': u_ids
                                                              })

    assert resp.status_code == 403

def test_user_adding_themselves(clear_data, create_data):
    token, user_id_0, _, _, _ = create_data

    dm_create_data = requests.post(config.url + 'dm/create/v1', json={
                                                                         'token': token,
                                                                         'u_ids': [user_id_0]
                                                                        })
    assert dm_create_data.status_code == 400
