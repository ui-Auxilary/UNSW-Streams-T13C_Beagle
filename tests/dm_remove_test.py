#dm_remove_v1(token, dm_id)

import pytest

import json
import requests
from src import config

'''
InputError when:
      
  dm_id does not refer to a valid DM
      
AccessError when:
      
  dm_id is valid and the authorised user is not the original DM creator

Parameters:{ token, dm_id }
Return Type:{}
'''

def test_simple_case():
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

    requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_1,
                                                            'dm_id': dm_id
                                                            })
    
def test_non_creator():
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

    requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_2,
                                                            'dm_id': dm_id
                                                            })
    assert (resp.status_code == 403)

def test_invalid_dm_id():
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

    requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_1,
                                                            'dm_id': not_dm_id
                                                            })
    assert (resp.status_code == 400)

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

    requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_1,
                                                            'dm_id': dm_id_2
                                                            })

    requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_1,
                                                            'dm_id': dm_id_1
                                                            })