import pytest

import json
import requests
from src import config

'''
Invalid case when:
    - User does not exist
'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_data():
    register_user_1 = requests.post(config.url + 'auth/register/v2', json = { 'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })
                                                        
    token_1 = json.loads(register_user_1.text)['token'] 
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    register_user_2 = requests.post(config.url + 'auth/register/v2', json = { 'email': 'email2@gmail.com',
                                                                                'password': 'zxcvbnm',
                                                                                'name_first': 'christian',
                                                                                'name_last': 'lam'
                                                                              })
                                       
    token_2 = json.loads(register_user_2.text)['token']
    user_id_2 = json.loads(register_user_2.text)['auth_user_id']


    register_user_3 = requests.post(config.url + 'auth/register/v2', json = { 'email': 'email3@gmail.com',
                                                                                'password': 'something',
                                                                                'name_first': 'john',
                                                                                'name_last': 'doe'
                                                                              })
                                       
    token_3 = json.loads(register_user_3.text)['token']
    user_id_3 = json.loads(register_user_3.text)['auth_user_id']    

    return token_1, user_id_1, token_2, user_id_2, token_3, user_id_3

def test_single_dm(clear_data, create_data):
    token_1, _, _, user_id_2, _, _ = create_data

    ## create a DM
    create_dm = requests.post(config.url + 'dm/create/v1', json = { 'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    
    create_dm_id = json.loads(create_dm.text)['dm_id']

    ## get list of dms
    get_list = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1})
                                                  
    dm_data = json.loads(get_list.text)['dms']

    dm_list_id = dm_data[0]['dm_id'] 
    dm_list_name = dm_data[0]['name']

    ## get dm_details
    dm_detail_data = requests.get(config.url + 'dm/details/v1', params = { 
                                                                          'token': token_1,
                                                                          'dm_id': create_dm_id
                                                                         })

    dm_details_name = json.loads(dm_detail_data.text)['name']
    

    assert dm_list_id == create_dm_id
    assert dm_list_name == dm_details_name

def test_no_dms(clear_data, create_data):
    token_1, _, _, _, _, _ = create_data

    get_list = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1
                                                                })

    dm_list = json.loads(get_list.text)['dms']

    assert dm_list == []

def test_multiple_dms(clear_data, create_data):
    token_1, _, token_2, user_id_2, token_3, user_id_3 = create_data

    create_dm_1 = requests.post(config.url + 'dm/create/v1', json = { 'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    
    dm_id_1 = json.loads(create_dm_1.text)['dm_id']

    create_dm_2 = requests.post(config.url + 'dm/create/v1', json = { 'token': token_1,
                                                                      'u_ids': [user_id_3]
                                                                    })
    
    dm_id_2 = json.loads(create_dm_2.text)['dm_id']

    get_list = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1
                                                                })    
    dm_list_1 = json.loads(get_list.text)['dms']

    get_list = requests.get(config.url + 'dm/list/v1', params = { 'token': token_2
                                                                })
    dm_list_2 = json.loads(get_list.text)['dms']

    get_list = requests.get(config.url + 'dm/list/v1', params = { 'token': token_3
                                                                })
    dm_list_3 = json.loads(get_list.text)['dms']

    assert {'name': 'christianlam, lawrencelee', 'dm_id': dm_id_1} in dm_list_1
    assert {'name': 'johndoe, lawrencelee', 'dm_id': dm_id_2} in dm_list_1
    assert {'name': 'christianlam, lawrencelee', 'dm_id': dm_id_1} in dm_list_2
    assert {'name': 'johndoe, lawrencelee', 'dm_id': dm_id_2} in dm_list_3

def test_invalid_token(clear_data, create_data):
    get_list = requests.get(config.url + 'dm/list/v1', params = { 'token': 'token_4'
                                                                })

    assert  get_list.status_code == 403
  
def test_group_dm(clear_data, create_data):    
    token_1, _, _, user_id_2, _, user_id_3 = create_data

    create_dm = requests.post(config.url + 'dm/create/v1', json = { 'token': token_1,
                                                                      'u_ids': [user_id_2, user_id_3]
                                                                    })
    
    dm_id = json.loads(create_dm.text)['dm_id']

    get_list = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1
                                                                })
    
    dm_list = json.loads(get_list.text)['dms']
    assert dm_list[0] == {'name': 'christianlam, johndoe, lawrencelee',
                          'dm_id': dm_id}