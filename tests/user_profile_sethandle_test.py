#user_profile_sethandle(token, handle_str):

import pytest

import json
import requests
from src import config

'''
InputError when any of:      
    - length of handle_str is not between 3 and 20 characters inclusive
    - handle_str contains characters that are not alphanumeric
    - the handle is already used by another user
'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_data(clear_data):
    register_user_1 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })
                                                        
    token_1 = json.loads(register_user_1.text)
    token_1 = token_1['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']    

    register_user_2 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'email2@gmail.com',
                                                                                'password': 'zxcvbnm',
                                                                                'name_first': 'christian',
                                                                                'name_last': 'lam'
                                                                              })
                                       
    token_2 = json.loads(register_user_2.text)
    token_2 = token_2['token']    

    return token_1, token_2, user_id_1

def test_valid_handle_edit(clear_data, create_data):
    token_1, _, user_id = create_data

    ## set a new handle
    update_handle = requests.put(config.url + 'user/profile/sethandle/v1', params = {'token' : token_1,
                                                                                    'handle_str': 'watersheep'})
    assert update_handle.status_code == 200

    ## verify that the new handle is set
    user_info = requests.get(config.url + 'user/profile/v1', params = {'token' : token_1,
                                                                           'u_id'  : user_id})

    print(json.loads(user_info.text))
    new_handle = json.loads(user_info.text)['user']['handle_str']

    assert new_handle == 'watersheep'

def test_handle_taken(clear_data, create_data):
    _, token_2, _ = create_data
    
    update_handle = requests.put(config.url + 'user/profile/sethandle/v1', params = {'token' : token_2,
                                                                                    'handle_str': 'lawrencelee'})

    assert update_handle.status_code == 400

def test_too_long(clear_data, create_data):
    token_1, _, _ = create_data

    update_handle = requests.put(config.url + 'user/profile/sethandle/v1', params = {'token' : token_1,
                                                                                    'handle_str': 'watersheepmightbealittletoolong'})

    assert update_handle.status_code == 400

def test_too_short(clear_data, create_data):
    token_1, _, _ = create_data

    update_handle = requests.put(config.url + 'user/profile/sethandle/v1', params = {'token' : token_1,
                                                                                    'handle_str': 'ah'})

    assert update_handle.status_code == 400

def test_non_alphanumeric(clear_data, create_data):
    token_1, _, _ = create_data

    update_handle = requests.put(config.url + 'user/profile/sethandle/v1', params = { 'token' : token_1,
                                                                                    'handle_str': 'watersheep$$'})

    assert update_handle.status_code == 400

def test_invalid_token(clear_data, create_data):
    update_handle = requests.put(config.url + 'user/profile/sethandle/v1', params = {'token' : 'token_1',
                                                                                    'handle_str': 'watersheep'})

    assert update_handle.status_code == 403
