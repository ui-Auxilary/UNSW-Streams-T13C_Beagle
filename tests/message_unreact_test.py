#message/unreact/v1

import pytest

import requests
from src import config
import json

'''
Parameters:{ token, message_id, react_id }

InputError when any of:
    - message_id is not a valid message within a channel or DM that the authorised user has joined
    - react_id is not a valid react ID
    - the message does not contain a react with ID react_id from the authorised user

AccessError when any of:
    - invalid_id

Return Type:{}
'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
        'email': 'hello@mycompany.com',
        'password': 'mypassword',
        'name_first': 'Firstname',
        'name_last': 'Lastname'
    })

    # stores a token
    token = json.loads(register_data.text)['token']

    # create a channel with that user
    channel_create_data = requests.post(config.url + 'channels/create/v2', json={
        'token': token,
        'name': 'channel_1',
        'is_public': True
    })

    channel_id = json.loads(channel_create_data.text)['channel_id']

    # register another user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
        'email': 'HELLO@mycompany.com',
        'password': 'MYpassword',
        'name_first': 'FirstNAME',
        'name_last': 'LastNAME'
    })

    # stores a token
    token2 = json.loads(register_data.text)['token']
    user_2_id = json.loads(register_data.text)['auth_user_id']

    # add user_2 to the channel
    requests.post(config.url + 'channel/join/v2', json={
        'token': token2,
        'channel_id': channel_id
    })

    # stores a string
    channel_message = "Hello, I don't know what I am doing. Send help. xoxo."

    # user_2 sends a message
    message_send_data = requests.post(config.url + 'message/send/v1', json={
        'token': token2,
        'channel_id': channel_id,
        'message': channel_message
    })

    channel_messages = [json.loads(message_send_data.text)['message_id']]
    # send random messages
    for message in range(0, 5):
        message_send_data = requests.post(config.url + 'message/send/v1', json={
            'token': token,
            'channel_id': channel_id,
            'message': f"This is message:{message}"
        })
        message_id = json.loads(message_send_data.text)['message_id']
        channel_messages.append(message_id)

    # create a dm with that user
    dm_create_data = requests.post(config.url + 'dm/create/v1', json={
        'token': token,
        'u_ids': [user_2_id]
    })

    dm_id = json.loads(dm_create_data.text)['dm_id']

    # stores a string
    dm_message = "That dough go uwu"
    
    dm_messages = []
    # send random messages
    for message in range(0, 5):
        # user_2 sends a message
        message_send_data = requests.post(config.url + 'message/senddm/v1', json={
        'token': token,
        'dm_id': dm_id,
        'message': dm_message[message]
    })
        message_id = json.loads(message_send_data.text)['message_id']
        dm_messages.append(message_id)

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
        'email': 'hsdfdsello@mycompany.com',
        'password': 'mypdfsfassword',
        'name_first': 'Firsdfsdstname',
        'name_last': 'Lasfdsftname'
    })

    # stores a token
    memberless_token = json.loads(register_data.text)['token']

    # reacts to messages
    requests.post(config.url + 'message/react/v1', json={
        'token': token,
        'message_id': channel_messages[1],
        'react_id': 1
    })

    requests.post(config.url + 'message/react/v1', json={
        'token': token,
        'message_id': channel_messages[2],
        'react_id': 1
    })

    requests.post(config.url + 'message/react/v1', json={
        'token': token,
        'message_id': channel_messages[5],
        'react_id': 1
    })

    requests.post(config.url + 'message/react/v1', json={
        'token': token,
        'message_id': dm_messages[1],
        'react_id': 1
    })

    requests.post(config.url + 'message/react/v1', json={
        'token': token,
        'message_id': dm_messages[2],
        'react_id': 1
    })

    requests.post(config.url + 'message/react/v1', json={
        'token': token,
        'message_id': dm_messages[4],
        'react_id': 1
    })

    return token, channel_messages, dm_messages, channel_id, dm_id, memberless_token, token2

def test_simple_case_channel(clear_data, create_data):
    token, channel_messages, _, channel_id, _, _, _ = create_data
    requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': channel_messages[1],
        'react_id': 1
    })

    requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': channel_messages[2],
        'react_id': 1
    })

    requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': channel_messages[5],
        'react_id': 1
    })

    # get the messages in the channel
    channel_message_data = requests.get(config.url + 'channel/messages/v2', params={
        'token': token,
        'channel_id': channel_id,
        'start': 0
    })

    length = len(channel_messages) - 1
    channel_react = json.loads(channel_message_data.text)['messages'][length - 1]['reacts']
    assert channel_react != 1
    channel_react = json.loads(channel_message_data.text)['messages'][length - 2]['reacts']
    assert channel_react != 1
    channel_react = json.loads(channel_message_data.text)['messages'][length - 5]['reacts']
    assert channel_react != 1

def test_simple_case_dm(clear_data, create_data):
    token, _, dm_messages, _, dm_id, _, _ = create_data
    requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': dm_messages[1],
        'react_id': 1
    })

    requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': dm_messages[2],
        'react_id': 1
    })

    requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': dm_messages[4],
        'react_id': 1
    })

    # get the messages in the dm
    dm_message_data = requests.get(config.url + 'dm/messages/v1', params={
        'token': token,
        'dm_id': dm_id,
        'start': 0
    })
    
    length = len(dm_messages) - 1
    channel_react = json.loads(dm_message_data.text)['messages'][length - 1]['reacts']
    assert channel_react != 1
    channel_react = json.loads(dm_message_data.text)['messages'][length - 2]['reacts']
    assert channel_react != 1
    channel_react = json.loads(dm_message_data.text)['messages'][length - 4]['reacts']
    assert channel_react != 1

def test_user_is_not_channel_member(clear_data, create_data):
    _, channel_messages, _, _, _, memberless_token, _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': memberless_token,
        'message_id': channel_messages[1],
        'react_id': 1
    })
    assert react_data.status_code == 400

def test_user_is_not_dm_member(clear_data, create_data):
    _, _, dm_messages, _, _, memberless_token, _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': memberless_token,
        'message_id': dm_messages[1],
        'react_id': 1
    })
    assert react_data.status_code == 400

def test_invalid_message_id(clear_data, create_data):
    token, _, _, _, _, _ , _ = create_data
    message_id = 93232
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': message_id,
        'react_id': 1
    })
    assert react_data.status_code == 400

def test_invalid_react_id_number_channel(clear_data, create_data):
    token, channel_messages, _, _, _, _ , _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': channel_messages[0],
        'react_id': 34
    })
    assert react_data.status_code == 400

def test_invalid_react_id_number_dm(clear_data, create_data):
    token, _, dm_messages, _, _, _ , _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': dm_messages[0],
        'react_id': -1
    })
    assert react_data.status_code == 400

def test_invalid_react_id_string_channel(clear_data, create_data):
    token, channel_messages, _, _, _, _ , _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': channel_messages[0],
        'react_id': "dshjkfskjd"
    })
    assert react_data.status_code == 400

def test_invalid_react_id_string_dm(clear_data, create_data):
    token, _, dm_messages, _, _, _ , _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': dm_messages[0],
        'react_id': "dshjkfskjd"
    })
    assert react_data.status_code == 400

def test_unreact_already_unreacted_message_channel(clear_data, create_data):
    token, channel_messages, _, _, _, _ , _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': channel_messages[0],
        'react_id': 1
    })
    assert react_data.status_code == 400

def test_unreact_already_unreacted_message_dm(clear_data, create_data):
    token, _, dm_messages, _, _, _ , _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': dm_messages[0],
        'react_id': 1
    })
    assert react_data.status_code == 400

def test_double_unreact_channel(clear_data, create_data):
    token, channel_messages, _, _, _, _, _ = create_data

    requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': channel_messages[1],
        'react_id': 1
    })
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': channel_messages[1],
        'react_id': 1
    })
    assert react_data.status_code == 400

def test_double_unreact_dm(clear_data, create_data):
    token, _, dm_messages, _, _, _, _ = create_data

    requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': dm_messages[0],
        'react_id': 1
    })
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token,
        'message_id': dm_messages[0],
        'react_id': 1
    })
    assert react_data.status_code == 400

def test_unauthorised_user_channel(clear_data, create_data):
    _, channel_messages, _, _, _, _, token2 = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token2,
        'message_id': channel_messages[0],
        'react_id': 1
    })
    assert react_data.status_code == 400

def test_unauthorised_user_dm(clear_data, create_data):
    _, _, dm_messages, _, _, _, token2 = create_data

    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': token2,
        'message_id': dm_messages[1],
        'react_id': 1
    })
    assert react_data.status_code == 400

def test_invalid_token_channel(clear_data,create_data):
    _, channel_messages, _, _, _, _ , _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': "random_string",
        'message_id': channel_messages[0],
        'react_id': 1
    })
    assert react_data.status_code == 403

def test_invalid_token_dm(clear_data,create_data):
    _, _, dm_messages, _, _, _ , _ = create_data
    react_data = requests.post(config.url + 'message/unreact/v1', json={
        'token': "random_string",
        'message_id': dm_messages[0],
        'react_id': 1
    })
    assert react_data.status_code == 403