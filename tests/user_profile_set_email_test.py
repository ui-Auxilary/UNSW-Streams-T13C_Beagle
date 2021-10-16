#user_profile_setemail(token, email):

import pytest

import json
import requests
from src import config

'''
InputError when any of:      
    - email entered is not a valid email
    - email address is already being used by another user
'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_data():
    register_user_1 = requests.post(config.url + 'auth/register/v2', json= {    'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })
                                                        
    token_1 = json.loads(register_user_1.text)['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    requests.post(config.url + 'auth/register/v2', json= {    'email': 'email2@gmail.com',
                                                                                'password': 'zxcvbnm',
                                                                                'name_first': 'christian',
                                                                                'name_last': 'lam'
                                                                              })


    return token_1, user_id_1

def test_simple_case(clear_data, create_data):
    token_1, user_data = create_data
    
    update_email = requests.put(config.url + 'user/profile/setemail/v1', json= {    'token' : token_1,
                                                                                    'email': 'newemail@gmail.com'})

    assert update_email.status_code == 200

    ## verify that the new handle is set
    user_info = requests.get(config.url + 'user/profile/v1', params = {'token' : token_1,
                                                                       'u_id'  : user_data})

    new_email = json.loads(user_info.text)['user']['email']

    assert new_email == 'newemail@gmail.com'

def test_already_used(clear_data, create_data):
    token_1, _ = create_data

    update_email = requests.put(config.url + 'user/profile/setemail/v1', json= {    'token' : token_1,
                                                                                    'email': 'email2@gmail.com'})

    assert update_email.status_code == 400

def test_invalid_email(clear_data, create_data):
    token_1, _ = create_data
    
    update_email = requests.put(config.url + 'user/profile/setemail/v1', json= {    'token' : token_1,
                                                                                    'email': 'newemail'})

    assert update_email.status_code == 400