import pytest

from src import config
import requests
import json

'''
InputError when:
      
    - dm_id does not refer to a valid DM
      
AccessError when:
      
    - dm_id is valid and the authorised user is not a member of the DM

'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
                                                                           'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # gets user_id
    auth_user_id = json.loads(register_data.text)['auth_user_id']

    # stores a token
    token = json.loads(register_data.text)['token']

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

    u_ids = [user_id_1, user_id_2]

    # gets dm_id
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': token,
                                                                 'u_ids': u_ids
                                                               })

    dm_id = json.loads(dm_data.text)['dm_id']

    return auth_user_id, user_id_1, token, dm_id, u_ids

def test_invalid_token(clear_data, create_data):
    _, _,  _, dm_id, _ = create_data
    dm_details = requests.get(config.url + 'dm/details/v1', params={
                                                       'token': 'Hey yo',
                                                       'dm_id': dm_id
                                                      })
                                                                                
    assert dm_details.status_code == 403

def test_simple_case(clear_data, create_data):
    auth_user_id, user_id_1, user_token, dm_id, _ = create_data

    ## get the user's data
    user_profile_data = requests.get(config.url + 'user/profile/v1', params={
                                                                        'token': user_token,
                                                                        'u_id': auth_user_id 
                                                                       })
    
    auth_user_profile = json.loads(user_profile_data.text)['user']

    user_2_profile_data = requests.get(config.url + 'user/profile/v1', params={
                                                                        'token': user_token,
                                                                        'u_id': user_id_1 
                                                                       })
    
    user_2_profile = json.loads(user_2_profile_data.text)['user']

    ## get information about the channel
    dm_detail_data = requests.get(config.url + 'dm/details/v1', params={
                                                                        'token': user_token,
                                                                        'dm_id': dm_id
                                                                       })

    dm_detail = json.loads(dm_detail_data.text)

    dm_name = dm_detail['name']
    dm_members = dm_detail['members']

    dm_data = {
        'dm_id': dm_id,
        'name': dm_name
    }

    ## get information about the dm
    dm_list_data = requests.get(config.url + 'dm/list/v1', params={
                                                                    'token': user_token,
                                                                  })

    dm_list = json.loads(dm_list_data.text)['dms']

    assert dm_data in dm_list
    assert auth_user_profile in dm_members
    assert user_2_profile in dm_members

def test_invalid_dm_id(clear_data, create_data):
    _, _, token, _, _ = create_data
    dm_id = 43989

    resp = requests.get(config.url + 'dm/details/v1', params={'token': token,
                                                              'dm_id': dm_id
                                                              })

    assert resp.status_code == 400

def test_invalid_user(clear_data, create_data):
    _, _, _, dm_id, _ = create_data

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'iuwafhO@mycompany.com',
                                                                           'password': 'msdfewed',
                                                                           'name_first': 'dfsds',
                                                                           'name_last': 'sdddsfs'
                                                                           })
    # stores a token
    token2 = json.loads(register_data.text)['token']

    resp = requests.get(config.url + 'dm/details/v1', params={'token': token2,
                                                              'dm_id': dm_id
                                                              })

    assert resp.status_code == 403

def test_both_invalid_dm_id_and_user(clear_data):
    dm_id = 43989

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'iuwafhO@mycompany.com',
                                                                           'password': 'msdfewed',
                                                                           'name_first': 'dfsds',
                                                                           'name_last': 'sdddsfs'
                                                                           })
    # stores a token
    token2 = json.loads(register_data.text)['token']

    resp = requests.get(config.url + 'dm/details/v1', params={'token': token2,
                                                              'dm_id': dm_id
                                                              })

    assert resp.status_code == 400

@pytest.mark.skip("Dependant test not implemented")
def test_user_leaves(clear_data, create_data):
    auth_user_id, user_id_1, user_token, dm_id, _ = create_data

    ## get the user's data
    user_profile_data = requests.get(config.url + 'user/profile/v1', params={
                                                                        'token': user_token,
                                                                        'u_id': auth_user_id 
                                                                       })
    
    auth_user_profile = json.loads(user_profile_data.text)['user']

    user_2_profile_data = requests.get(config.url + 'user/profile/v1', params={
                                                                        'token': user_token,
                                                                        'u_id': user_id_1 
                                                                       })

    ## User 1 leaves the channel
    requests.post(config.url + 'dm/leave/v1', json={
                                                      'token': user_token,
                                                      'dm_id': dm_id
                                                     })

    ## get information about the channel
    dm_detail_data = requests.get(config.url + 'dm/details/v1', params={
                                                                        'token': user_token,
                                                                        'dm_id': dm_id
                                                                       })

    dm_detail = json.loads(dm_detail_data.text)

    dm_name = dm_detail['name']
    dm_members = dm_detail['members']

    dm = {
        'dm_id': dm_id,
        'name': dm_name
    }

    ## get information about the dm
    dm_list_data = requests.get(config.url + 'dm/list/v1', params={
                                                                    'token': user_token,
                                                                  })

    dm_list = json.loads(dm_list_data.text)['dms']

    assert dm in dm_list
    assert auth_user_profile not in dm_members
    assert user_2_profile_data in dm_members

@pytest.mark.skip("Dependant test not implemented")
def test_delete_channel_and_details(clear_data, create_data):
    auth_user_id, user_id_1, user_token, dm_id, _ = create_data

    ## get the user's data
    requests.get(config.url + 'user/profile/v1', params={
                                                         'token': user_token,
                                                         'u_id': auth_user_id 
                                                        })

    requests.get(config.url + 'user/profile/v1', params={
                                                         'token': user_token,
                                                         'u_id': user_id_1 
                                                        })

    ## Delete the DM
    requests.delete(config.url + 'dm/remove/v1', json={
                                                         'token': user_token,
                                                         'dm_id': dm_id
                                                        })
    ## get information about the channel
    requests.get(config.url + 'dm/details/v1', params={
                                                       'token': user_token,
                                                       'dm_id': dm_id
                                                      })