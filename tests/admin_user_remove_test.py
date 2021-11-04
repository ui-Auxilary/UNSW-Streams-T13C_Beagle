# admin_user_remove(token, u_id):

import pytest

import json
import requests
from src import config
from src.data_operations import get_user

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
def create_private_channels(create_users):
    token_1, _, token_2, _ = create_users
    create_channel = requests.post(config.url + 'channels/create/v2', json={
        'token': token_1,
        'name': 'Global_owner_channel',
        'is_public': False
    })

    channel_id = json.loads(create_channel.text)['channel_id']

    create_channel_2 = requests.post(config.url + 'channels/create/v2', json={
        'token': token_2,
        'name': 'random',
        'is_public': False
    })
    channel_id_2 = json.loads(create_channel_2.text)['channel_id']

    return channel_id, channel_id_2


@pytest.fixture
def create_dms(create_users):
    token_1, _, token_2, user_id_2 = create_users
    create_dm = requests.post(config.url + 'dm/create/v1', json={
        'token': token_1,
        'u_ids': [user_id_2]
    })
    dm_id = json.loads(create_dm.text)['dm_id']

    create_message = requests.post(config.url + 'message/senddm/v1', json={
        'token': token_2,
        'dm_id': dm_id,
        'message': 'wee woo haha'
    })

    message_id = json.loads(create_message.text)['message_id']

    return dm_id, message_id


def test_simple_case(clear_data, create_users):
    token_1, _, token_2, user_id_2 = create_users

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_2
    })

    # check user can't get their own token
    get_user_profile = requests.get(config.url + 'user/profile/v1', params={
        'token': token_2,
        'u_id': user_id_2
    })

    assert get_user_profile.status_code == 403

    get_user_profile = requests.get(config.url + 'user/profile/v1', params={
        'token': token_1,
        'u_id': user_id_2
    })

    user_profile = json.loads(get_user_profile.text)['user']

    assert user_profile == {
        'u_id': user_id_2,
        'name_first': 'Removed',
        'name_last': 'user',
        'email': '',
        'handle_str': '',
        'profile_img_url': '',
    }


def test_removed_user_in_private_channel(clear_data, create_users, create_private_channels):
    token_1, user_id_1, token_2, user_id_2 = create_users
    channel_id, _ = create_private_channels

    # user_1 invites user_2 to the channel
    requests.post(config.url + 'channel/invite/v2', json={
        'token': token_1,
        'channel_id': channel_id,
        'u_id': user_id_2
    })

    create_message_0 = requests.post(config.url + 'message/send/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'message': 'first message'
    })

    create_message = requests.post(config.url + 'message/send/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'message': 'one more message'
    })

    assert create_message.status_code == 200
    message_id = json.loads(create_message_0.text)['message_id']
    message_id_2 = json.loads(create_message.text)['message_id']

    requests.post(config.url + 'message/send/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'message': 'one more message'
    })

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_2
    })

    check_message = requests.get(config.url + 'channel/messages/v2', params={
        'token': token_1,
        'channel_id': channel_id,
        'start': 0
    })

    messages = json.loads(check_message.text)['messages']

    time_created = json.loads(check_message.text)[
        'messages'][len(messages) - message_id]['time_created']
    time_created_2 = json.loads(check_message.text)[
        'messages'][len(messages) - message_id_2]['time_created']

    message_data = {
        'message_id': message_id,
        'u_id': user_id_1,
        'message': 'first message',
        'time_created': time_created
    }

    message_data_2 = {
        'message_id': message_id_2,
        'u_id': user_id_2,
        'message': 'Removed user',
        'time_created': time_created_2
    }

    assert message_data in messages
    assert message_data_2 in messages

    # get the user data
    user_profile_data = requests.get(config.url + 'user/profile/v1', params={
        'token': token_1,
        'u_id': user_id_2
    })
    # get channel details and check that user 2 is not in it
    user_2_profile = json.loads(user_profile_data.text)['user']

    # get information about the channel
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
        'token': token_1,
        'channel_id': channel_id
    })

    channel_members = json.loads(channel_detail_data.text)['all_members']

    assert user_2_profile not in channel_members


def test_removed_user_using_command(clear_data, create_users):
    token_1, _, token_2, user_id_2 = create_users

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_2
    })

    get_user_profile = requests.get(config.url + 'user/profile/v1', params={
        'token': token_2,
        'u_id': user_id_2
    })

    assert get_user_profile.status_code == 403


def test_member_of_dm(clear_data, create_users, create_dms):
    token_1, _, token_2, user_id_2 = create_users
    dm_id, message_id = create_dms

    requests.post(config.url + 'message/senddm/v1', json={
        'token': token_2,
        'dm_id': dm_id,
        'message': 'another message'
    })

    create_message = requests.post(config.url + 'message/senddm/v1', json={
        'token': token_2,
        'dm_id': dm_id,
        'message': 'one more message'
    })
    message_id_2 = json.loads(create_message.text)['message_id']

    requests.post(config.url + 'message/senddm/v1', json={
        'token': token_1,
        'dm_id': dm_id,
        'message': 'one more message'
    })

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_2
    })

    check_message = requests.get(config.url + 'dm/messages/v1', params={
        'token': token_1,
        'dm_id': dm_id,
        'start': 0
    })

    messages = json.loads(check_message.text)['messages']

    print(messages)

    time_created = json.loads(check_message.text)[
        'messages'][len(messages) - message_id]['time_created']
    time_created_2 = json.loads(check_message.text)[
        'messages'][len(messages) - message_id_2]['time_created']

    message_data = {
        'message_id': message_id,
        'u_id': user_id_2,
        'message': 'Removed user',
        'time_created': time_created
    }

    message_data_2 = {
        'message_id': message_id_2,
        'u_id': user_id_2,
        'message': 'Removed user',
        'time_created': time_created_2
    }

    assert message_data in messages
    assert message_data_2 in messages


def test_member_of_channel(clear_data, create_users, create_channel):
    token_1, user_id_1, token_2, user_id_2 = create_users
    channel_id, _ = create_channel

    # user_2 joins the channel
    requests.post(config.url + 'channel/join/v2', json={
        'token': token_2,
        'channel_id': channel_id
    })

    create_message_0 = requests.post(config.url + 'message/send/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'message': 'first message'
    })

    create_message = requests.post(config.url + 'message/send/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'message': 'one more message'
    })

    assert create_message.status_code == 200
    message_id = json.loads(create_message_0.text)['message_id']
    message_id_2 = json.loads(create_message.text)['message_id']

    requests.post(config.url + 'message/send/v1', json={
        'token': token_1,
        'channel_id': channel_id,
        'message': 'one more message'
    })

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_2
    })

    check_message = requests.get(config.url + 'channel/messages/v2', params={
        'token': token_1,
        'channel_id': channel_id,
        'start': 0
    })

    messages = json.loads(check_message.text)['messages']

    time_created = json.loads(check_message.text)[
        'messages'][len(messages) - message_id]['time_created']
    time_created_2 = json.loads(check_message.text)[
        'messages'][len(messages) - message_id_2]['time_created']

    message_data = {
        'message_id': message_id,
        'u_id': user_id_1,
        'message': 'first message',
        'time_created': time_created
    }

    message_data_2 = {
        'message_id': message_id_2,
        'u_id': user_id_2,
        'message': 'Removed user',
        'time_created': time_created_2
    }

    assert message_data in messages
    assert message_data_2 in messages

def test_create_multiple_dms(clear_data, create_users):
    token_1, user_id_1, token_2, user_id_2 = create_users

    ## create 2 dms, and send messages in both
    create_dm = requests.post(config.url + 'dm/create/v1', json={
        'token': token_1,
        'u_ids': [user_id_2]
    })

    dm_id = json.loads(create_dm.text)['dm_id']

    requests.post(config.url + 'message/senddm/v1', json={
        'token': token_2,
        'dm_id': dm_id,
        'message': 'wee woo haha'
    })

    create_dm_2 = requests.post(config.url + 'dm/create/v1', json={
        'token': token_2,
        'u_ids': [user_id_1]
    })

    dm_id_2 = json.loads(create_dm_2.text)['dm_id']
    
    ## get the profile of user_2
    resp = requests.get(config.url + 'user/profile/v1',
                        params={'token': token_1, 'u_id': user_id_2})


    user_2_profile = json.loads(resp.text)['user']

    ## remove user 2
    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_2
    })

    ## check that user doesn't show up in dm_members
    dm_details = requests.get(config.url + 'dm/details/v1', params={
                                                       'token': token_1,
                                                       'dm_id': dm_id
                                                      })

    dm_details_2 = requests.get(config.url + 'dm/details/v1', params={
                                                       'token': token_1,
                                                       'dm_id': dm_id_2
                                                      })

    dm_members = json.loads(dm_details.text)['members']
    dm_members_2 = json.loads(dm_details_2.text)['members']

    assert user_2_profile not in dm_members
    assert user_2_profile not in dm_members_2

def test_channel_owner(clear_data, create_users, create_channel):
    token_1, user_id_1, token_2, user_id_2 = create_users

    # Create a channel with user_2 as the sole owner of channel_id_2
    create_channel = requests.post(config.url + 'channels/create/v2', json={
        'token': token_2,
        'name': 'random',
        'is_public': True
    })

    channel_id = json.loads(create_channel.text)['channel_id']

    # user_1 joins the channel
    requests.post(config.url + 'channel/join/v2', json={
        'token': token_1,
        'channel_id': channel_id
    })

    # channel owner, adds Stream owner as another owner of their channel
    add_owner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'u_id': user_id_1
    })

    assert add_owner.status_code == 200

    # Streams owner removes User 2
    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_2
    })

    # Check that channel 'random' still exists, but no longer has user
    channel_details = requests.get(config.url + 'channel/details/v2', params={
        'token': token_1,
        'channel_id': channel_id
    })

    # Get user profiles
    global_owner_profile = requests.get(config.url + 'user/profile/v1', params={
        'token': token_1,
        'u_id': user_id_1
    })

    get_user_profile = requests.get(config.url + 'user/profile/v1', params={
        'token': token_1,
        'u_id': user_id_2
    })

    user_owner = json.loads(global_owner_profile.text)['user']
    user_profile = json.loads(get_user_profile.text)['user']

    # Check that the Streams user is the only owner and member of that channel
    channel_owners = json.loads(channel_details.text)['owner_members']
    channel_members = json.loads(channel_details.text)['all_members']

    assert user_owner in channel_owners
    assert user_owner in channel_members
    assert user_profile not in channel_members

    # Check that removed user has the right profile details
    all_users = requests.get(config.url + 'users/all/v1', params={
        'token': token_1
    })
    users = json.loads(all_users.text)['users']

    assert user_profile == {
        'u_id': user_id_2,
        'name_first': 'Removed',
        'name_last': 'user',
        'email': '',
        'handle_str': '',
        'profile_img_url': ''        
    }

    assert user_owner in users
    assert user_profile not in users


def test_remove_sole_channel_owner(clear_data, create_users, create_channel):
    token_1, user_id_1, token_2, user_id_2 = create_users

    # Create a channel with user_2 as the sole owner of channel_id_2
    create_channel = requests.post(config.url + 'channels/create/v2', json={
        'token': token_2,
        'name': 'random',
        'is_public': True
    })
    channel_id = json.loads(create_channel.text)['channel_id']

    # Global owner removes User_2
    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_2
    })

    # Check that channel_2 exists, but has neither owner nor members
    all_channel_data = requests.get(config.url + 'channels/listall/v2', params={
        'token': token_1
    })

    all_channels = json.loads(all_channel_data.text)['channels']

    # check that the channel still exists
    assert any(('channel_id', channel_id) in channel.items()
               for channel in all_channels)

    global_owner_profile = requests.get(config.url + 'user/profile/v1', params={
        'token': token_1,
        'u_id': user_id_1
    })

    get_user_profile = requests.get(config.url + 'user/profile/v1', params={
        'token': token_1,
        'u_id': user_id_2
    })

    owner_profile = json.loads(global_owner_profile.text)['user']
    user_profile = json.loads(get_user_profile.text)['user']

    all_users = requests.get(
        config.url + 'users/all/v1', params={'token': token_1})

    users = json.loads(all_users.text)['users']

    assert user_profile == {
        'u_id': user_id_2,
        'name_first': 'Removed',
        'name_last': 'user',
        'email': '',
        'handle_str': '',
        'profile_img_url': '',
    }

    assert user_profile not in users
    assert owner_profile in users


def test_invalid_user_id(clear_data, create_users):
    token_1, _, _, _ = create_users
    remove_user = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': 549848
    })
    assert remove_user.status_code == 400


def test_remove_only_owner(clear_data, create_users):
    token_1, user_id_1, _, _ = create_users
    remove_user = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_1
    })
    assert remove_user.status_code == 400


def test_invalid_permissions(clear_data, create_users):
    _, user_id_1, token_2, _ = create_users
    remove_user = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_2,
        'u_id': user_id_1
    })
    assert remove_user.status_code == 403


def test_invalid_token(clear_data, create_users):
    _, _, _, user_id_2 = create_users

    remove_user = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': 'token_1',
        'u_id': user_id_2
    })
    assert remove_user.status_code == 403


@pytest.mark.skip("Whitebox testing")
def test_send_edit_message_then_remove_user(clear_data, create_users, create_dms):
    token_1, _, token_2, user_id_2 = create_users
    dm_id, _ = create_dms

    requests.post(config.url + 'message/senddm/v1', json={
        'token': token_2,
        'dm_id': dm_id,
        'message': 'another message'
    })

    create_message = requests.post(config.url + 'message/senddm/v1', json={
        'token': token_1,
        'dm_id': dm_id,
        'message': 'one more message'
    })

    message_id_2 = json.loads(create_message.text)['message_id']

    requests.post(config.url + 'message/senddm/v1', json={
        'token': token_1,
        'dm_id': dm_id,
        'message': 'one more message'
    })

    # user_2 edits message_2
    requests.put(config.url + 'message/edit/v1', json={
        'token': token_1,
        'message_id': message_id_2,
        'message': "Sponegebob squarepants"
    })

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token_1,
        'u_id': user_id_2
    })

    check_message = requests.get(config.url + 'dm/messages/v1', params={
        'token': token_1,
        'dm_id': dm_id,
        'start': 0
    })

    json.loads(check_message.text)['messages']
    pass
