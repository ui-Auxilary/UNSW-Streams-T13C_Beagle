import pytest

from src import config
import requests
import json
import time

'''
Sending a message to get buffered in the standup queue, assuming a standup is currently active. 
Note: We do not expect @ tags to be parsed as proper tags when sending to standup/send

InputError when:

    - channel_id does not refer to a valid channel
    - length of message is over 1000 characters
    - an active standup is not currently running in the channel

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
def user_and_channel_data(register_user_data):
    _, user_token, _, user_token_2 = register_user_data

    # create a public channel with global_owner
    channel_data = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token,
        'name': 'Public_owner_channel',
        'is_public': True
    })

    channel_id = json.loads(channel_data.text)['channel_id']

    # user_2 creates a public and private channel
    channel_data_2 = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token_2,
        'name': 'Public_user_channel',
        'is_public': True
    })

    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    # create a channel with that user
    channel_data_3 = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token_2,
        'name': 'Private_user_channel',
        'is_public': False
    })

    channel_id_3 = json.loads(channel_data_3.text)['channel_id']

    return user_token, user_token_2, channel_id, channel_id_2, channel_id_3

# ___SIMPLE TEST CASES - NO DEPENDANT FUNCTIONS___ #


def test_simple_case_public_channel(clear_data, user_and_channel_data):
    auth_token, _, channel_1, _, _ = user_and_channel_data

    requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 20
    })

    # send a message to the startup
    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'message': "Hello there!"
    })

    # check the request is valid
    assert standup_send_data.status_code == 200


def test_simple_case_private_channel(clear_data, user_and_channel_data):
    _, user_token_2, _, _, channel_3 = user_and_channel_data

    # start an active startup
    requests.post(config.url + 'standup/start/v1', json={
        'token': user_token_2,
        'channel_id': channel_3,
        'length': 10
    })

    # send a message to the startup
    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': user_token_2,
        'channel_id': channel_3,
        'message': "Hello world"
    })
    # check the request is valid

    assert standup_send_data.status_code == 200


# ___COMPLEX TEST CASES - DEPENDANT FUNCTIONS___ #

def test_send_multiple_messages_active_standup(clear_data, register_user_data, user_and_channel_data):
    _, _, user_2_id, _ = register_user_data
    auth_token, user_2_token, _, channel_2, _ = user_and_channel_data

    # auth_user creates a startup in channel_1
    requests.post(config.url + 'standup/start/v1', json={
        'token': user_2_token,
        'channel_id': channel_2,
        'length': 5
    })

    # send a few messages to the startup
    requests.post(config.url + 'standup/send/v1', json={
        'token': user_2_token,
        'channel_id': channel_2,
        'message': "Hello there!"
    })

    requests.post(config.url + 'standup/send/v1', json={
        'token': user_2_token,
        'channel_id': channel_2,
        'message': "Hello again!"
    })

    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': user_2_token,
        'channel_id': channel_2,
        'message': "Bye there!"
    })

    # check the request is valid
    assert standup_send_data.status_code == 200

    # get the profile of the user who sent the messages
    user_profile_data = requests.get(config.url + 'user/profile/v1', params={
        'token': auth_token,
        'u_id': user_2_id
    })

    user_handle = json.loads(user_profile_data.text)['user']['handle_str']

    # Simulate waiting for the standup to be over
    time.sleep(5)

    # get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
        'token': user_2_token,
        'channel_id': channel_2,
        'start': 0
    })

    channel_messages = json.loads(channel_message_data.text)['messages']
    channel_end = json.loads(channel_message_data.text)['end']

    print(channel_messages)
    assert channel_messages[0]['u_id'] == user_2_id
    assert channel_messages[0]['message'] == f"{user_handle}: Hello there!\n{user_handle}: Hello again!\n{user_handle}: Bye there!"
    assert channel_end == -1


def test_multiple_users_send_multiple_messages_standup(clear_data, register_user_data, user_and_channel_data):
    auth_user_id, _, user_id_2, _ = register_user_data
    auth_token, user_token_2, channel_1, _, _ = user_and_channel_data

    # user_2 joins channel_1 and starts a standup
    requests.post(config.url + 'channel/join/v2', json={
        'token': user_token_2,
        'channel_id': channel_1
    })

    # auth_user creates a startup in channel_1
    requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 5
    })

    # both users send a few messages to the startup
    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': user_token_2,
        'channel_id': channel_1,
        'message': "a"
    })

    # check the request is valid
    assert standup_send_data.status_code == 200

    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'message': "b"
    })

    requests.post(config.url + 'standup/send/v1', json={
        'token': user_token_2,
        'channel_id': channel_1,
        'message': "c"
    })

    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'message': "d"
    })

    # check the request is valid
    assert standup_send_data.status_code == 200

    # get the profile of both users
    user_profile_data = requests.get(config.url + 'user/profile/v1', params={
        'token': auth_token,
        'u_id': auth_user_id
    })

    user_profile_data_2 = requests.get(config.url + 'user/profile/v1', params={
        'token': auth_token,
        'u_id': user_id_2
    })

    user_handle = json.loads(user_profile_data.text)['user']['handle_str']
    user_handle_2 = json.loads(user_profile_data_2.text)['user']['handle_str']

    # Simulate waiting for the standup to be over
    time.sleep(5)

    # get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
        'token': auth_token,
        'channel_id': channel_1,
        'start': 0
    })

    channel_messages = json.loads(channel_message_data.text)['messages']
    channel_end = json.loads(channel_message_data.text)['end']

    print(channel_messages)
    assert channel_messages[0]['u_id'] == auth_user_id
    assert channel_messages[0]['message'] == f"{user_handle_2}: a\n{user_handle}: b\n{user_handle_2}: c\n{user_handle}: d"
    assert channel_end == -1

# ___TEST VALID INPUT___ #


def test_invalid_channel_id(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': auth_token,
        'channel_id': 123,
        'message': "Hello world"
    })

    assert standup_send_data.status_code == 400


def test_length_message_over_1000_characters(clear_data, user_and_channel_data):
    auth_token, _, channel_1, _, _ = user_and_channel_data

    # auth_user creates a valid standup
    requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 60
    })

    # auth_user sends a message that is over 1000 characters
    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'message': "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Na"
    })

    assert standup_send_data.status_code == 400


def test_valid_channel_no_active_standup(clear_data, user_and_channel_data):
    auth_token, _, channel_1, _, _ = user_and_channel_data

    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'message': "Hello world"
    })

    assert standup_send_data.status_code == 400

# ___TEST ACCESS PERMISSIONS ___ #


def test_valid_channel_user_not_channel_member(clear_data, user_and_channel_data):
    _, _, channel_1, _, _ = user_and_channel_data

    # register another user not in the channel
    register_data_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'user3@gmail.com',
        'password': 'user3password',
        'name_first': 'User',
        'name_last': '3'
    })

    user_token_3 = json.loads(register_data_3.text)['token']

    # user_3 tries to start a standup in the channel
    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': user_token_3,
        'channel_id': channel_1,
        'message': "This ain't it chief"
    })

    assert standup_send_data.status_code == 403

# ___ TEST BOTH INPUT AND ACCESS ERRORS __ #


def test_user_not_channel_member_and_length_message_invalid(clear_data, user_and_channel_data):
    auth_token, _, channel_1, _, _ = user_and_channel_data

    # register another user not in the channel
    register_data_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'user3@gmail.com',
        'password': 'user3password',
        'name_first': 'User',
        'name_last': '3'
    })

    user_id_3 = json.loads(register_data_3.text)['auth_user_id']

    # auth_user creates a valid standup
    requests.post(config.url + 'standup/start/v1', json={
        'token': auth_token,
        'channel_id': channel_1,
        'length': 60
    })

    # user_id_3 sends a message that is over 1000 characters to standup
    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': user_id_3,
        'channel_id': channel_1,
        'message': "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Na"
    })

    assert standup_send_data.status_code == 403


def test_no_active_standup_in_channel_and_user_not_member(clear_data, user_and_channel_data):
    _, _, channel_1, _, _ = user_and_channel_data

    # register another user not in the channel
    register_data_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'user3@gmail.com',
        'password': 'user3password',
        'name_first': 'User',
        'name_last': '3'
    })

    token_3 = json.loads(register_data_3.text)['token']

    # user_3 tries to send a message to standup
    standup_send_data = requests.post(config.url + 'standup/send/v1', json={
        'token': token_3,
        'channel_id': channel_1,
        'message': "This ain't it chief"
    })

    assert standup_send_data.status_code == 403
