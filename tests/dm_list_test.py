#dm_list_v1(token)

import pytest

import json
import requests
from src import config

'''
Invalid case when:
    - User does not exist
'''

def test_single_dm():
    register_user_1 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })
                                                        
    token_1 = json.loads(register_user_1.text)['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    register_user_2 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'email2@gmail.com',
                                                                                'password': 'zxcvbnm',
                                                                                'name_first': 'christian',
                                                                                'name_last': 'lam'
                                                                              })
                                       
    token_2 = json.loads(register_user_2.text)['token']
    user_id_2 = json.loads(register_user_2.text)['auth_user_id']

    create_dm = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    
    dm_id = json.loads(create_dm.text)['dm_id']

    get_list = requests.get(config.url + 'dm/list/v1', param = { 'token': token_1
                                                                })
    
    dm_list = json.loads(get_list.text)['dms']

def test_no_dms():
    register_user_1 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })
                                                        
    token_1 = json.loads(register_user_1.text)['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    get_list = requests.get(config.url + 'dm/list/v1', param = { 'token': token_1
                                                                })
    
    dm_list = json.loads(get_list.text)['dms']

def test_multiple_dms():
    register_user_1 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })
                                                        
    token_1 = json.loads(register_user_1.text)['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    register_user_2 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'email2@gmail.com',
                                                                                'password': 'zxcvbnm',
                                                                                'name_first': 'christian',
                                                                                'name_last': 'lam'
                                                                              })
                                       
    token_2 = json.loads(register_user_2.text)['token']
    user_id_2 = json.loads(register_user_2.text)['auth_user_id']

    register_user_3 = requests.post(config.url + 'auth/register/v2', params = { 'email': 'email3@gmail.com',
                                                                                'password': 'something',
                                                                                'name_first': 'john',
                                                                                'name_last': 'doe'
                                                                              })
                                       
    token_3 = json.loads(register_user_3.text)['token']
    user_id_3 = json.loads(register_user_3.text)['auth_user_id']

    create_dm_1 = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    
    dm_id_1 = json.loads(create_dm_1.text)['dm_id']

    create_dm_2 = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_3]
                                                                    })
    
    dm_id_2 = json.loads(create_dm_2.text)['dm_id']

    get_list_1 = requests.get(config.url + 'dm/list/v1', param = { 'token': token_1
                                                                })    
    dm_list_1 = json.loads(get_list.text)['dms']

    get_list_2 = requests.get(config.url + 'dm/list/v1', param = { 'token': token_2
                                                                })
    dm_list_2 = json.loads(get_list.text)['dms']

    get_list_3 = requests.get(config.url + 'dm/list/v1', param = { 'token': token_3
                                                                })
    dm_list_3 = json.loads(get_list.text)['dms']

def test_invalid_token():
    get_list = requests.get(config.url + 'dm/list/v1', param = { 'token': token_4
                                                                })
    
    dm_list = json.loads(get_list.text)['dms']

    assert  (resp.status_code == 400)