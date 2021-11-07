import pytest

from src import config
import requests
import json

'''
For a given channel, return whether a standup is active in it, and what time the standup finishes. 
If no standup is active, then time_finish returns None.

InputError when:

    - channel_id does not refer to a valid channel

AccessError when:

    - channel_id is valid and the authorised user is not a member of the channel
        ie. Global owner has permissions, but is not in the channel

'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def register_user_data():
    register_data = requests.post(config.url + 'auth/register/v2', json={
        'email': 'joemama@gmail.com',
        'password': 'hijoeitsmama',
        'name_first': 'Joe',
        'name_last': 'Mama'
    })

    auth_user_id = json.loads(register_data.text)['auth_user_id']
    user_token = json.loads(register_data.text)['token']

    register_data_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'bobbyjones@gmail.com',
        'password': 'dillywillywobbo123',
        'name_first': 'Bobby',
        'name_last': 'Jones'
    })

    user_id_2 = json.loads(register_data_2.text)['auth_user_id']
    user_token_2 = json.loads(register_data_2.text)['token']

    return auth_user_id, user_token, user_id_2, user_token_2


@pytest.fixture
def userprofile_and_channel_data(clear_data, register_user_data):
    auth_user_id, user_token, user_id_2, user_token_2 = register_user_data

    # get user_profile data
    auth_user_profile_data = requests.get(config.url + 'user/profile/v1',
                        params={'token': user_token, 'u_id': auth_user_id})

    user_2_profile_data = requests.get(config.url + 'user/profile/v1',
                        params={'token': user_token_2, 'u_id': user_id_2})

    auth_user_profile = json.loads(auth_user_profile_data.text)['user']
    user_2_profile = json.loads(user_2_profile_data.text)['user']

    # create a public channel with global_owner
    channel_data = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token,
        'name': 'Public_owner_channel',
        'is_public': True
    })

    channel_id = json.loads(channel_data.text)['channel_id']

    # create a channel with user_2
    channel_data_2 = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token_2,
        'name': 'Private_user_channel',
        'is_public': False
    })

    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    return auth_user_profile, user_token, user_2_profile, user_token_2, channel_id, channel_id_2

# ___COMPLEX TEST CASES - SEVERAL DEPENDANT FUNCTIONS___ #

def test_user_invite_channel_notification(clear_data, userprofile_and_channel_data):
    auth_user_profile, user_token, user_2_profile, user_token_2, channel_id, _ = userprofile_and_channel_data

    ## get auth_user and user_2's id and handle
    auth_user_id = auth_user_profile['u_id']
    auth_user_handle = auth_user_profile['handle_str']

    user_2_id = user_2_profile['u_id']
    user_2_handle = user_2_profile['handle_str']

    ## user_1 invites user_2 to channel 1
    channel_invite_data = requests.post(config.url + 'channel/invite/v2', json={
                                                            'token': user_token,
                                                            'channel_id': channel_id,
                                                            'u_id': user_2_id
                                                            })
    
    ## get channel details
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                 'token': user_token,
                                                                                 'channel_id': channel_id
                                                                                })

    channel_detail = json.loads(channel_detail_data.text)

    channel_name = channel_detail['name']

    ## get user_2 notifications
    notification_get_data = requests.get(config.url + 'notifications/get/v1', params={
                                                                                      'token': user_token_2
                                                                                     })
    
    assert notification_get_data.status_code == 200

    notifications = json.loads(notification_get_data.text)['notifications']

    assert notifications == [{'channel_id': channel_id, 'dm_id': -1, 'notification_message': f"{auth_user_handle} added you to {channel_name}"}]

def test_user_add_dm_notification(clear_data, register_user_data):
    auth_user_id, user_token, user_id_2, user_token_2 = register_user_data

    # get user_profile data
    auth_user_profile_data = requests.get(config.url + 'user/profile/v1',
                        params={'token': user_token, 'u_id': auth_user_id})

    auth_user_profile = json.loads(auth_user_profile_data.text)['user']
    auth_user_handle = auth_user_profile['handle_str']

    # create a public channel with global_owner
    dm_create_data = requests.post(config.url + 'dm/create/v1', json={
                                                                       'token': user_token,
                                                                       'u_ids': [user_id_2]
                                                                     })

    dm_id = json.loads(dm_create_data.text)['dm_id']

    ## get user_2 notifications
    notification_get_data = requests.get(config.url + 'notifications/get/v1', params={
                                                                                      'token': user_token_2
                                                                                     })
    
    assert notification_get_data.status_code == 200

    notifications = json.loads(notification_get_data.text)['notifications']

    ## get information about the dm
    dm_detail_data = requests.get(config.url + 'dm/details/v1', params={
                                                                        'token': user_token,
                                                                        'dm_id': dm_id
                                                                       })

    dm_detail = json.loads(dm_detail_data.text)

    dm_name = dm_detail['name']

    assert notifications == [{'channel_id': -1, 'dm_id': dm_id, 'notification_message': f"{auth_user_handle} added you to {dm_name}"}]

def test_user_channel_tag_notification(clear_data, userprofile_and_channel_data):
    auth_user_profile, user_token, user_2_profile, user_token_2, channel_id, _ = userprofile_and_channel_data

    ## get auth_user and user_2's id and handle
    auth_user_id = auth_user_profile['u_id']
    auth_user_handle = auth_user_profile['handle_str']

    user_2_id = user_2_profile['u_id']
    user_2_handle = user_2_profile['handle_str']

    ## user_1 invites user_2 to channel 1
    channel_invite_data = requests.post(config.url + 'channel/invite/v2', json={
                                                            'token': user_token,
                                                            'channel_id': channel_id,
                                                            'u_id': user_2_id
                                                            })
    
    ## get channel details
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                 'token': user_token,
                                                                                 'channel_id': channel_id
                                                                                })

    channel_detail = json.loads(channel_detail_data.text)

    channel_name = channel_detail['name']

    message = f"@{user_2_handle} joe mama went to school then she graduated and she went to sawcon deez nutz"
    message_first_20 = message[0:20]
    ## auth_user sends user 2 a message
    requests.post(config.url + 'message/send/v1', json={
                                                        'token': user_token,
                                                        'channel_id': channel_id,
                                                        'message':  message
                                                       })

    ## get user_2 notifications
    notification_get_data = requests.get(config.url + 'notifications/get/v1', params={
                                                                                      'token': user_token_2
                                                                                     })
    
    assert notification_get_data.status_code == 200

    notifications = json.loads(notification_get_data.text)['notifications']

    assert notifications == [{'channel_id': channel_id, 'dm_id': -1, 'notification_message': f"{auth_user_handle} tagged you in {channel_name}: {message[:20]}"}, 
                             {'channel_id': channel_id, 'dm_id': -1, 'notification_message': f"{auth_user_handle} added you to {channel_name}"}]

def test_user_react_message_channel_notification(clear_data, userprofile_and_channel_data):
    auth_user_profile, user_token, user_2_profile, user_token_2, channel_id, _ = userprofile_and_channel_data

    ## get auth_user and user_2's id and handle
    auth_user_id = auth_user_profile['u_id']
    auth_user_handle = auth_user_profile['handle_str']

    user_2_id = user_2_profile['u_id']
    user_2_handle = user_2_profile['handle_str']

    ## user_1 invites user_2 to channel 1
    channel_invite_data = requests.post(config.url + 'channel/invite/v2', json={
                                                            'token': user_token,
                                                            'channel_id': channel_id,
                                                            'u_id': user_2_id
                                                            })
    
    ## get channel details
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
                                                                                 'token': user_token,
                                                                                 'channel_id': channel_id
                                                                                })

    channel_detail = json.loads(channel_detail_data.text)

    channel_name = channel_detail['name']

    ## user_2 sends a message and user_1 reacts to it
    send_message_data = requests.post(config.url + 'message/send/v1', json={
        'token': user_token_2,
        'channel_id': channel_id,
        'message': "Hey guys welcome back to faze clan"
    })

    message_id = json.loads(send_message_data.text)['message_id']

    message_react_data = requests.post(config.url + 'message/react/v1', json={
        'token': user_token,
        'message_id': message_id,
        'react_id': 1
    })

    assert message_react_data.status_code == 200

    ## get user_2 notifications
    notification_get_data = requests.get(config.url + 'notifications/get/v1', params={
                                                                                      'token': user_token_2
                                                                                     })
    
    assert notification_get_data.status_code == 200

    notifications = json.loads(notification_get_data.text)['notifications']

    assert notifications == [{'channel_id': channel_id, 'dm_id': -1, 'notification_message': f"{auth_user_handle} reacted to your message in {channel_name}"}, 
    {'channel_id': channel_id, 'dm_id': -1, 'notification_message': f"{auth_user_handle} added you to {channel_name}"}]

def test_user_dm_react_notifications(clear_data, register_user_data):
    auth_user_id, user_token, user_id_2, user_token_2 = register_user_data

    # get user_profile data
    auth_user_profile_data = requests.get(config.url + 'user/profile/v1',
                        params={'token': user_token, 'u_id': auth_user_id})

    auth_user_profile = json.loads(auth_user_profile_data.text)['user']
    auth_user_handle = auth_user_profile['handle_str']

    # create a public channel with global_owner
    dm_create_data = requests.post(config.url + 'dm/create/v1', json={
                                                                       'token': user_token,
                                                                       'u_ids': [user_id_2]
                                                                     })

    dm_id = json.loads(dm_create_data.text)['dm_id']

    ## user_2 sends a dm and user_1 reacts to it
    message_data = requests.post(config.url + 'message/senddm/v1', json={
                                                                         'token': token,
                                                                         'dm_id': dm_id,
                                                                         'message': message
                                                                         })

    message_id = json.loads(message_data.text)['message_id']

    message_react_data = requests.post(config.url + 'message/react/v1', json={
        'token': user_token,
        'message_id': message_id,
        'react_id': 1
    })

    assert message_react_data.status_code == 200

    ## get user_2 notifications
    notification_get_data = requests.get(config.url + 'notifications/get/v1', params={
                                                                                      'token': user_token_2
                                                                                     })
    
    assert notification_get_data.status_code == 200

    notifications = json.loads(notification_get_data.text)['notifications']

    ## get information about the dm
    dm_detail_data = requests.get(config.url + 'dm/details/v1', params={
                                                                        'token': user_token,
                                                                        'dm_id': dm_id
                                                                       })

    dm_detail = json.loads(dm_detail_data.text)

    dm_name = dm_detail['name']

    assert notifications == [{'channel_id': -1, 'dm_id': dm_id, 'notification_message': f"{auth_user_handle} reacted to your message in {dm_name}",
    {'channel_id': -1, 'dm_id': dm_id, 'notification_message': f"{auth_user_handle} added you to {dm_name}"}]