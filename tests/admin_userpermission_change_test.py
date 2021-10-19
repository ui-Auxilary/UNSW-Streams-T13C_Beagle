#admin_user_remove(token, u_id):

import pytest

import json
import requests
from src import config

'''
InputError when any of:
    - u_id does not refer to a valid user
    - u_id refers to a user who is the only global owner

AccessError when:
    - the authorised user is not a global owner

TestCases:
    - (removing user from all channels they were a member of) check not a member of any channels user was previously in
    - (removing only owner of channel) check that the channel has no owners or members [x]
    - (remove user from channel and dms with messages) check message sender is 'Removed user'

'''

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_users():
    register_user_1 = requests.post(config.url + 'auth/register/v2', json = { 
                                                                                'email': 'asd@gmail.com',
                                                                                'password': 'qwertyuiop',
                                                                                'name_first': 'lawrence',
                                                                                'name_last': 'lee'
                                                                              })

    token_1 = json.loads(register_user_1.text)['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    register_user_2 = requests.post(config.url + 'auth/register/v2', json = { 
                                                                                'email': 'email2@gmail.com',
                                                                                'password': 'zxcvbnm',
                                                                                'name_first': 'christian',
                                                                                'name_last': 'lam'
                                                                              })

    token_2 = json.loads(register_user_2.text)['token']
    user_id_2 = json.loads(register_user_2.text)['auth_user_id']

    return token_1, user_id_1, token_2, user_id_2

@pytest.fixture
def create_channel(create_users):
    token_1, _, token_2, _ = create_users
    create_channel = requests.post(config.url + 'channels/create/v2', json={
                                                                              'token': token_1,
                                                                              'name': 'Global_owner_channel',
                                                                              'is_public': True
                                                                             })

    channel_id = json.loads(create_channel.text)['channel_id']

    create_channel_2 = requests.post(config.url + 'channels/create/v2', json={
                                                                              'token': token_2,
                                                                              'name': 'random',
                                                                              'is_public': True
                                                                             })
    channel_id_2 = json.loads(create_channel_2.text)['channel_id']

    return channel_id, channel_id_2

@pytest.fixture
def create_dms(create_users):
    token_1, _, token_2, user_id_2 = create_users
    create_dm = requests.post(config.url + 'dm/create/v1', json ={
                                                                      'token': token_1,
                                                                      'u_ids': [user_id_2]
                                                                    })
    dm_id = json.loads(create_dm.text)['dm_id']

    create_message = requests.post(config.url + 'message/senddm/v1', json = {
                                                                              'token': token_2,
                                                                              'dm_id': dm_id,
                                                                              'message': 'wee woo haha'
                                                                            })

    message_id = json.loads(create_message.text)['message_id']

    return dm_id, message_id

def test_simple_case(clear_data, create_users, create_channel):
    token_1, user_id_1, token_2, user_id_2 = create_users
    channel_id_1, _ = create_channel

    register_user_3 = requests.post(config.url + 'auth/register/v2', json = { 
                                                                                'email': 'aboosd@gmail.com',
                                                                                'password': 'qwer24324tyuiop',
                                                                                'name_first': 'Xidisfsi',
                                                                                'name_last': 'adasdas'
                                                                              })

    _ = json.loads(register_user_3.text)['token']
    user_id_3 = json.loads(register_user_3.text)['auth_user_id']

    ## add user_2 and user_3 to channel_1's channel
    requests.post(config.url + 'channel/invite/v2', json={
                                                          'token': token_1,
                                                          'channel_id': channel_id_1,
                                                          'u_id': user_id_2
                                                         })

    requests.post(config.url + 'channel/invite/v2', json={
                                                          'token': token_1,
                                                          'channel_id': channel_id_1,
                                                          'u_id': user_id_3
                                                         })

    ## promote user_3 to channel owner
    requests.post(config.url + 'channel/addowner/v1', json={
                                                          'token': token_1,
                                                          'channel_id': channel_id_1,
                                                          'u_id': user_id_3
                                                         })

    ## check that user has no permissions
    remove_channel_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                             'token': token_2,
                                                                             'channel_id': channel_id_1,
                                                                             'u_id': user_id_1
                                                                            })

    assert remove_channel_owner.status_code == 403

    ## change permissions of user_2 to be global owner
    requests.post(config.url + 'admin/userpermission/change/v1', json = {
                                                                         'token': token_1,
                                                                         'u_id': user_id_2,
                                                                         'permission_id': 1
                                                                        })

    ## check that user_2 can now remove user_1 as the channel owner
    remove_channel_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                             'token': token_2,
                                                                             'channel_id': channel_id_1,
                                                                             'u_id': user_id_1
                                                                            })

    assert remove_channel_owner.status_code == 200

    channel_details_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                      'token': token_2,
                                                                                      'channel_id': channel_id_1,
                                                                                     })

    channel_owners = json.loads(channel_details_data.text)['owner_members']

    ## check that user_1 is no longer a channel owner
    assert any(('u_id', user_id_1) in owner.items() for owner in channel_owners) == False

def test_owner_demotes_owner(clear_data, create_users, create_channel):
    token_1, user_id_1, token_2, user_id_2 = create_users
    channel_id_1, _ = create_channel

    ## add user_2 to channel_1's channel
    requests.post(config.url + 'channel/invite/v2', json={
                                                          'token': token_1,
                                                          'channel_id': channel_id_1,
                                                          'u_id': user_id_2
                                                         })

    ## check that user has no permissions
    remove_channel_owner = requests.post(config.url + 'channel/removeowner/v1', json={
                                                                             'token': token_2,
                                                                             'channel_id': channel_id_1,
                                                                             'u_id': user_id_1
                                                                            })

    assert remove_channel_owner.status_code == 403

    ## change permissions of user_2 to be global owner
    requests.post(config.url + 'admin/userpermission/change/v1', json = {
                                                                         'token': token_1,
                                                                         'u_id': user_id_2,
                                                                         'permission_id': 1
                                                                        })

    ## user_2 demotes user_1
    change_permissions = requests.post(config.url + 'admin/userpermission/change/v1', json = {
                                                                         'token': token_2,
                                                                         'u_id': user_id_1,
                                                                         'permission_id': 2
                                                                        })

    assert change_permissions.status_code == 200

     ## check that user_1 has no permissions
    remove_channel_owner = requests.delete(config.url + 'admin/user/remove/v1', json={
                                                                                    'token': token_1,
                                                                                    'u_id': user_id_2
                                                                                   })

    assert remove_channel_owner.status_code == 403

def test_invalid_permissions(clear_data, create_users):
    token_1, user_id_1, _, _ = create_users
    change_permissions = requests.post(config.url + 'admin/userpermission/change/v1', json={
                                                                                'token': token_1,
                                                                                'u_id': user_id_1,
                                                                                'permission_id': 5
                                                                              })
    assert change_permissions.status_code == 400

def test_invalid_user_id(clear_data, create_users):
    token_1, _, _, _ = create_users
    change_permissions = requests.post(config.url + 'admin/userpermission/change/v1', json={
                                                                                'token': token_1,
                                                                                'u_id': 549848,
                                                                                'permission_id': 1
                                                                              })
    assert change_permissions.status_code == 400

def test_demote_only_owner(clear_data, create_users):
    token_1, user_id_1, _, _ = create_users
    change_permissions = requests.post(config.url + 'admin/userpermission/change/v1', json={
                                                                                'token': token_1,
                                                                                'u_id': user_id_1,
                                                                                'permission_id': 2
                                                                              })
    assert change_permissions.status_code == 400

def test_invalid_token(clear_data, create_users):
    _, _, _, user_id_2 = create_users

    change_permissions = requests.delete(config.url + 'admin/user/remove/v1', json = {
                                                                    'token': 'token_1',
                                                                    'u_id': user_id_2,
                                                                    'permission_id': 1
                                                                  })
    assert change_permissions.status_code == 403
