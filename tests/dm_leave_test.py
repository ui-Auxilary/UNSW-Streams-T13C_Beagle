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

    # stores a token and user id
    auth_token = json.loads(register_data.text)['token']
    auth_user_id = json.loads(register_data.text)['auth_user_id']

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HELLOOO@mycompany.com',
                                                                         'password': 'MYPPassword',
                                                                         'name_first': 'FRSTName',
                                                                         'name_last': 'LSTName'
                                                                         })

    # gets user_id
    user_id_1 = json.loads(register_data.text)['auth_user_id']

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HLOOO@mycompany.com',
                                                                         'password': 'MYPPassWOrd',
                                                                         'name_first': 'FRSNme',
                                                                         'name_last': 'LSName'
                                                                         })

    # gets user_id
    user_id_2 = json.loads(register_data.text)['auth_user_id']

    user_token = json.loads(register_data.text)['token']

    u_ids = [user_id_1, user_id_2]

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'sfikshd@mycompany.com',
                                                                         'password': 'Msjkjksfd',
                                                                         'name_first': 'FRsdlkfme',
                                                                         'name_last': 'LSsjme'
                                                                         })

    # create a dm with the owner and users
    dm_create_data = requests.post(config.url + 'dm/create/v1', json={'token': auth_token,
                                                                      'u_ids': u_ids
                                                                      })

    dm_id = json.loads(dm_create_data.text)['dm_id']

    return auth_token, user_token, u_ids, dm_id, user_id_2, auth_user_id


def test_simple_case(clear_data, create_data):
    auth_token, user_token, _, dm_id, user_id_2, _ = create_data

    # get the dm details
    dm_details_data = requests.get(config.url + 'dm/details/v1', params={'token': user_token,
                                                                         'dm_id': dm_id
                                                                         })

    # get user data and check they are a member of the dm
    user_profile_data = requests.get(config.url + 'user/profile/v1', params={'token': user_token,
                                                                             'u_id': user_id_2
                                                                             })

    dm_details = json.loads(dm_details_data.text)['members']
    user_profile = json.loads(user_profile_data.text)['user']

    assert user_profile in dm_details

    # user leaves and is no longer a member of the dm
    requests.post(config.url + 'dm/leave/v1', json={'token': user_token,
                                                    'dm_id': dm_id,
                                                    })

    dm_details_data = requests.get(config.url + 'dm/details/v1', params={'token': auth_token,
                                                                         'dm_id': dm_id
                                                                         })

    dm_details = json.loads(dm_details_data.text)['members']
    assert user_profile not in dm_details


def test_creator_leaves(clear_data, create_data):
    auth_token, user_token, _, dm_id, _, auth_user_id = create_data

    # get a list of the dms the creator is in
    dm_list_data = requests.get(
        config.url + 'dm/list/v1', params={'token': auth_token})
    dms_list = json.loads(dm_list_data.text)['dms']

    # get user profiles
    user_profile_data = requests.get(config.url + 'user/profile/v1', params={
        'token': user_token,
        'u_id': auth_user_id
    })

    auth_user_profile = json.loads(user_profile_data.text)['user']

    # creator leaves the channel
    requests.post(config.url + 'dm/leave/v1', json={'token': auth_token,
                                                    'dm_id': dm_id,
                                                    })

    # check the creator is gone and the dm still exists
    dm_details_data = requests.get(config.url + 'dm/details/v1', params={'token': user_token,
                                                                         'dm_id': dm_id
                                                                         })

    dm_details = json.loads(dm_details_data.text)
    dm_members = dm_details['members']

    assert auth_user_profile not in dm_members
    assert dm_details not in dms_list


def test_invalid_dm_id(clear_data, create_data):
    auth_token, _, _, _, _, _ = create_data
    dm_id = 2380

    resp = requests.post(config.url + 'dm/leave/v1', json={'token': auth_token,
                                                           'dm_id': dm_id,
                                                           })

    assert resp.status_code == 400


def test_invalid_user(clear_data, create_data):
    _, _, _, dm_id, _, _ = create_data

    resp = requests.post(config.url + 'dm/leave/v1', json={'token': 'invalid_token',
                                                           'dm_id': dm_id,
                                                           })

    assert resp.status_code == 403


def test_both_invalid_dm_id_and_invalid_user(clear_data, create_data):
    invalid_dm_id = 2380

    resp = requests.post(config.url + 'dm/leave/v1', json={'token': 'invalid_token',
                                                           'dm_id': invalid_dm_id,
                                                           })

    assert resp.status_code == 403


def test_user_leave_dm_they_are_not_in(clear_data, create_data):
    _, _, _, dm_id, _, _ = create_data

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'another@mycompany.com',
                                                                         'password': 'mypassword',
                                                                         'name_first': 'Firstname',
                                                                         'name_last': 'Lastname'
                                                                         })

    # stores a token and user id
    auth_token_3 = json.loads(register_data.text)['token']

    # creator leaves the channel
    resp = requests.post(config.url + 'dm/leave/v1', json={'token': auth_token_3,
                                                           'dm_id': dm_id,
                                                           })
    assert resp.status_code == 403
