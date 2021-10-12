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
def create_data():
    register_user_1 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })
                                                        
    token_1 = json.loads(register_user_1.text)['token']    

    register_user_2 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'email2@gmail.com',
                                                                                'password': 'zxcvbnm',
                                                                                'name_first': 'christian',
                                                                                'name_last': 'lam'
                                                                              })
                                       
    token_2 = json.loads(register_user_2.text)['token']    

    return token_1, token_2

def test_simple_case(clear_data, create_data):
    token_1, _ = create_data

    update_handle = requests.put(config.url + 'user/profile/setemail/v1', params = {'token' : token_1,
                                                                                    'handle_str': 'watersheep'})

    assert (update_handle.status_code == 200)

def test_handle_taken(clear_data, create_data):
    _, token_2 = create_data
    
    update_handle = requests.put(config.url + 'user/profile/setemail/v1', params = {'token' : token_2,
                                                                                    'handle_str': 'lawrencelee'})

    assert (update_handle.status_code == 400)

def test_too_long(clear_data, create_data):
    token_1, _ = create_data

    update_handle = requests.put(config.url + 'user/profile/setemail/v1', params = {'token' : token_1,
                                                                                    'handle_str': 'watersheepmightbealittletoolong'})

    assert (update_handle.status_code == 400)

def test_too_short(clear_data, create_data):
    token_1, _ = create_data

    update_handle = requests.put(config.url + 'user/profile/setemail/v1', params = {'token' : token_1,
                                                                                    'handle_str': 'ah'})

    assert (update_handle.status_code == 400)

def test_non_alphanumeric(clear_data, create_data):
    token_1, _ = create_data

    update_handle = requests.put(config.url + 'user/profile/setemail/v1', params = { 'token' : token_1,
                                                                                    'handle_str': 'watersheep$$'})

    assert (update_handle.status_code == 400)