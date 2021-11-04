# channel_removeowner(token, channel_id, u_id):

import pytest

import json
import requests
from src import config

'''
InputError when any of:
    - channel_id does not refer to a valid channel[o]
    - u_id does not refer to a valid user[o]
    - u_id refers to a user who is not an owner of the channel[o]
    - u_id refers to a user who is currently the only owner of the channel[o]

    AccessError when:
    - channel_id is valid and the authorised user does not have owner permissions in the channel[o]

'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_users():
    register_user_1 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'asd@gmail.com',
        'password': 'qwertyuiop',
        'name_first': 'lawrence',
        'name_last': 'lee'
    })

    token_1 = json.loads(register_user_1.text)['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    register_user_2 = requests.post(config.url + 'auth/register/v2', json={
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
    token_1, _, _, user_2 = create_users
    create_channel = requests.post(config.url + 'channels/create/v2', json={
        'token': token_1,
        'name': 'channel',
        'is_public': True
    })
    channel_id = json.loads(create_channel.text)['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })
    return channel_id


def test_simple_case(clear_data, create_users, create_channel):
    token_1, user_1, _, user_2 = create_users

    channel_id = create_channel

    requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })
    assert remove_owner.status_code == 200

    channel_details = requests.get(config.url + 'channel/details/v2', params={
        'token': token_1,
        'channel_id': channel_id
    })
    owners = json.loads(channel_details.text)['owner_members']

    assert owners == [{'u_id': user_1,
                       'email': 'asd@gmail.com',
                       'name_first': 'lawrence',
                       'name_last': 'lee',
                       'handle_str': 'lawrencelee',
                       'profile_img_url': ''
                       }]


def test_add_channel_owner_already_owner(clear_data, create_users, create_channel):
    token_1, _, _, user_2 = create_users

    channel_id = create_channel

    # add user_2 as the owner
    add_channel_owner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })

    assert add_channel_owner.status_code == 200
    # add user_2 as the owner again
    add_channel_owner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })

    assert add_channel_owner.status_code == 400


def test_globalowner_nonmember_cant_add_public_channelowner(clear_data, create_users, create_channel):
    token_1, _, token_2, _ = create_users

    # user_2 creates a public channel and get the id
    create_channel = requests.post(config.url + 'channels/create/v2', json={
        'token': token_2,
        'name': 'channel',
        'is_public': True
    })

    channel_id = json.loads(create_channel.text)['channel_id']

    # register another user and make them join the channel
    register_user_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'email3@gmail.com',
        'password': 'zxcvbnm',
        'name_first': 'joe',
        'name_last': 'mama'
    })

    token_3 = json.loads(register_user_3.text)['token']
    user_id_3 = json.loads(register_user_3.text)['auth_user_id']

    # user_3 joins the channel as a member
    requests.post(config.url + 'channel/join/v2', json={
        'token': token_3,
        'channel_id': channel_id
    })

    # global_owner not in channel tries to add user_3 as a global owner
    add_channel_owner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_id_3
    })

    assert add_channel_owner.status_code == 403


def test_globalowner_nonmember_cant_add_private_channelower(clear_data, create_users, create_channel):
    token_1, _, token_2, _ = create_users

    # user_2 creates a public channel and get the id
    create_channel = requests.post(config.url + 'channels/create/v2', json={
        'token': token_2,
        'name': 'channel',
        'is_public': True
    })

    channel_id = json.loads(create_channel.text)['channel_id']

    # register another user and make them join the channel
    register_user_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'email3@gmail.com',
        'password': 'zxcvbnm',
        'name_first': 'joe',
        'name_last': 'mama'
    })

    user_id_3 = json.loads(register_user_3.text)['auth_user_id']

    # user_3 is invited and joins the private channel as a member
    channel_detail_data = requests.post(config.url + 'channel/invite/v2', json={
        'token': token_2,
        'channel_id': channel_id,
        'u_id': user_id_3
    })

    assert channel_detail_data.status_code == 200

    # global_owner not in channel tries to add user_3 as a global owner
    add_channel_owner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_id_3
    })

    assert add_channel_owner.status_code == 403


def test_globalowner_nonmember_cant_remove_owner(clear_data, create_users, create_channel):
    token_1, _, token_2, user_id_2 = create_users

    # user_2 creates a public channel and get the id
    create_channel = requests.post(config.url + 'channels/create/v2', json={
        'token': token_2,
        'name': 'channel',
        'is_public': True
    })

    channel_id = json.loads(create_channel.text)['channel_id']

    # global_owner not in channel tries to add user_3 as a global owner
    remove_channel_owner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_id_2
    })

    assert remove_channel_owner.status_code == 403


def test_add_channel_owner_non_channel_member(clear_data, create_users, create_channel):
    token_1, _, token_2, user_2 = create_users

    channel_id = create_channel

    # user_2 leaves the channel
    requests.post(config.url + 'channel/leave/v1', json={
        'token': token_2,
        'channel_id': channel_id,
    })

    # try to add user_2 as the owner
    add_channel = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })

    assert add_channel.status_code == 400


def test_invalid_channel_id(clear_data, create_users, create_channel):
    token_1, _, _, user_2 = create_users

    channel_id = create_channel

    requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token_1,
        'channel_id': 'not_channel_id',
        'u_id': user_2
    })
    assert remove_owner.status_code == 400


def test_adding_invalid_user(clear_data, create_users, create_channel):
    token_1, _, _, _ = create_users

    channel_id = create_channel

    add_owner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': 12314
    })

    assert add_owner.status_code == 400


def test_removing_invalid_user(clear_data, create_users, create_channel):
    token_1, _, _, user_2 = create_users

    channel_id = create_channel

    requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': 'not_user_id'
    })
    assert remove_owner.status_code == 400


def test_remove_non_owner(clear_data, create_users, create_channel):
    token_1, _, _, user_2 = create_users

    channel_id = create_channel

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })
    assert remove_owner.status_code == 400


def test_remove_only_owner(clear_data, create_users, create_channel):
    token_1, user_1, _, _ = create_users

    channel_id = create_channel

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_1
    })
    assert remove_owner.status_code == 400


def test_insufficient_permissions(clear_data, create_users, create_channel):
    _, user_1, token_2, _ = create_users

    channel_id = create_channel

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'u_id': user_1
    })
    assert remove_owner.status_code == 403


def test_invalid_token(clear_data, create_users, create_channel):
    _, _, _, user_2 = create_users

    channel_id = create_channel

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': 'token_1',
        'channel_id': channel_id,
        'u_id': user_2
    })
    assert remove_owner.status_code == 403


def test_remove_original_owner(clear_data, create_users, create_channel):
    token_1, user_1, token_2, user_2 = create_users

    channel_id = create_channel

    requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_2
    })

    remove_owner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'u_id': user_1
    })
    assert remove_owner.status_code == 200

    channel_details = requests.get(config.url + 'channel/details/v2', params={
        'token': token_1,
        'channel_id': channel_id
    })
    owners = json.loads(channel_details.text)['owner_members']

    assert owners == [{'u_id': user_2,
                       'email': 'email2@gmail.com',
                       'name_first': 'christian',
                       'name_last': 'lam',
                       'handle_str': 'christianlam',
                       'profile_img_url': ''}]


def test_channel_does_not_exist(clear_data, create_users, create_channel):
    token_1, _, _, user_2 = create_users

    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_1,
        'channel_id': 2342,
        'u_id': user_2
    })
    assert resp.status_code == 400


def test_user_not_authorised(clear_data, create_users, create_channel):
    _, _, token_2, user_2 = create_users
    channel_id = create_channel

    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'u_id': user_2
    })
    assert resp.status_code == 403
