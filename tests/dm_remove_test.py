
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

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_data():
    ## register users and extract their token and user id
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

    return token_1, user_id_1, token_2, user_id_2, token_3, user_id_3

def test_simple_case(clear_data, create_data):
    token_1, _, _, user_id_2, _, _ = create_data 

    ## create a dm with one other user
    create_dm = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    
    dm_id = json.loads(create_dm.text)['dm_id']

    ## remove user from dm
    remove_dm = requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_1,
                                                                        'dm_id': dm_id
                                                                        })

    assert remove_dm.status_code == 200

    ## check that the list of dm's the user is in is empty
    list_dms = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1 })

    get_list = json.loads(list_dms.text)['dms']
    assert get_list == []
    
def test_non_creator(clear_data, create_data):
    token_1, _, token_2, user_id_2, _, _ = create_data

    create_dm = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    
    dm_id = json.loads(create_dm.text)['dm_id']

    remove_dm = requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_2,
                                                                        'dm_id': dm_id
                                                                      })
    assert (remove_dm.status_code == 403)

def test_invalid_dm_id(clear_data, create_data):
    token_1, _, _, user_id_2, _, _ = create_data

    create_dm = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    json.loads(create_dm.text)['dm_id']

    remove_dm = requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_1,
                                                            'dm_id': 12213
                                                            })
    assert (remove_dm.status_code == 400)

def test_multiple_dms(clear_data, create_data):
    token_1, _, _, user_id_2, _, user_id_3 = create_data 

    create_dm_1 = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    
    dm_id_1 = json.loads(create_dm_1.text)['dm_id']

    create_dm_2 = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_3]
                                                                    })
    
    dm_id_2 = json.loads(create_dm_2.text)['dm_id']

    list_dms = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1
                                                                  })
    get_list = json.loads(list_dms.text)['dms']
    
    assert get_list == [{ 'dm_id': dm_id_1, 'name': 'christianlam, lawrencelee'},
                        { 'dm_id': dm_id_2, 'name': 'johndoe, lawrencelee'}]

    remove_dm = requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_1,
                                                            'dm_id': dm_id_2
                                                            })
    assert (remove_dm.status_code == 200)

    list_dms = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1
                                                                  })
    get_list = json.loads(list_dms.text)['dms']
    assert get_list == [{'dm_id': dm_id_1, 'name': 'christianlam, lawrencelee'}]

    remove_dm = requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_1,
                                                            'dm_id': dm_id_1
                                                            })
    assert (remove_dm.status_code == 200)
    
    list_dms = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1
                                                                  })
    get_list = json.loads(list_dms.text)['dms']
    assert get_list == []

def test_invalid_token(clear_data, create_data):
    token_1, _, _, user_id_2, _, _ = create_data 

    create_dm = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    
    dm_id = json.loads(create_dm.text)['dm_id']

    remove_dm = requests.delete(config.url + 'dm/remove/v1', params = { 'token': 'token_1',
                                                            'dm_id': dm_id
                                                            })

    assert (remove_dm.status_code == 403)

def test_group_dm(clear_data, create_data):
    token_1, _, _, user_id_2, _, user_id_3 = create_data 

    create_dm = requests.post(config.url + 'dm/create/v1', params = { 'token': token_1,
                                                                      'u_ids': [user_id_2, user_id_3]
                                                                    })
    
    dm_id = json.loads(create_dm.text)['dm_id']

    list_dms = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1
                                                                  })
    get_list = json.loads(list_dms.text)['dms']
    assert get_list == [{'dm_id': dm_id, 'name': 'christianlam, johndoe, lawrencelee'}]

    remove_dm = requests.delete(config.url + 'dm/remove/v1', params = { 'token': token_1,
                                                            'dm_id': dm_id
                                                            })
    assert (remove_dm.status_code == 200)
    list_dms = requests.get(config.url + 'dm/list/v1', params = { 'token': token_1
                                                                  })
    get_list = json.loads(list_dms.text)['dms']
    assert get_list == []
