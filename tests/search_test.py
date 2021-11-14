import pytest

import json
import requests
from src import config

'''
InputError when:
    - length of query_str is less than 1 or over 1000 characters

Test:
    - test single message with message as query_str [X]
    - test single message with a substring as query_str [X]
    - test no messages with query_str [X]
    - test message in channel and dm [X]
    - multiple channels and dms [X]
'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_users():
    register_user_1 = requests.post(config.url + 'auth/register/v2', json={'email': 'asd@gmail.com',
                                                                           'password': 'qwertyuiop',
                                                                           'name_first': 'lawrence',
                                                                           'name_last': 'lee'
                                                                           })

    token_1 = json.loads(register_user_1.text)['token']
    user_id_1 = json.loads(register_user_1.text)['auth_user_id']

    register_user_2 = requests.post(config.url + 'auth/register/v2', json={'email': 'email2@gmail.com',
                                                                           'password': 'zxcvbnm',
                                                                           'name_first': 'christian',
                                                                           'name_last': 'lam'
                                                                           })

    token_2 = json.loads(register_user_2.text)['token']
    user_id_2 = json.loads(register_user_2.text)['auth_user_id']

    register_user_3 = requests.post(config.url + 'auth/register/v2', json={'email': 'email3@gmail.com',
                                                                           'password': 'something',
                                                                           'name_first': 'john',
                                                                           'name_last': 'doe'
                                                                           })

    token_3 = json.loads(register_user_3.text)['token']
    user_id_3 = json.loads(register_user_3.text)['auth_user_id']

    return token_1, user_id_1, token_2, user_id_2, token_3, user_id_3


@pytest.fixture
def create_channels(create_users):
    token_1, _, _, user_2, _, user_3 = create_users
    create_channel_1 = requests.post(config.url + 'channels/create/v2', json={
        'token': token_1,
        'name': 'channel1',
        'is_public': True
    })
    channel_id_1 = json.loads(create_channel_1.text)['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={
        'token': token_1,
        'channel_id': channel_id_1,
        'u_id': user_2
    })

    create_channel_2 = requests.post(config.url + 'channels/create/v2', json={
        'token': token_1,
        'name': 'channel2',
        'is_public': True
    })
    channel_id_2 = json.loads(create_channel_2.text)['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={
        'token': token_1,
        'channel_id': channel_id_2,
        'u_id': user_3
    })
    return channel_id_1, channel_id_2


@pytest.fixture
def create_dms(create_users):
    token_1, _, token_2, user_id_2, _, user_id_3 = create_users

    create_dm_1 = requests.post(config.url + 'dm/create/v1', json={'token': token_1,
                                                                   'u_ids': [user_id_2]
                                                                   })

    dm_id_1 = json.loads(create_dm_1.text)['dm_id']

    create_dm_2 = requests.post(config.url + 'dm/create/v1', json={'token': token_1,
                                                                   'u_ids': [user_id_3]
                                                                   })

    dm_id_2 = json.loads(create_dm_2.text)['dm_id']

    create_dm_3 = requests.post(config.url + 'dm/create/v1', json={'token': token_2,
                                                                   'u_ids': [user_id_3]
                                                                   })

    dm_id_3 = json.loads(create_dm_3.text)['dm_id']

    return dm_id_1, dm_id_2, dm_id_3


# ___SIMPLE TEST CASES - NO DEPENDENT FUNCTIONS___ #


def test_single_message(clear_data, create_users, create_channels):
    token, user, _, _, _, _, = create_users
    channel_id, _ = create_channels
    message = "imagine"

    send_message_data = requests.post(config.url + 'message/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

    message_id = json.loads(send_message_data.text)['message_id']

    query_str = 'imagine'

    search = requests.get(config.url + 'search/v1', params={
        'token': token,
        'query_str': query_str
    })

    get_search = json.loads(search.text)['messages']

    assert get_search[0]['message_id'] == message_id
    assert get_search[0]['u_id'] == user
    assert get_search[0]['message'] == message
    assert get_search[0]['reacts'] == [{'is_this_user_reacted': False, 'react_id': 1, 'u_ids': []}]
    assert get_search[0]['is_pinned'] == False


def test_no_messages_from_query(clear_data, create_users, create_channels):
    token, _, _, _, _, _, = create_users
    _, _ = create_channels
    query_str = 'imagine'

    search = requests.get(config.url + 'search/v1', params={
        'token': token,
        'query_str': query_str
    })

    get_search = json.loads(search.text)['messages']

    assert get_search == []


def test_single_message_substring(clear_data, create_users, create_channels):
    token, user, _, _, _, _, = create_users
    channel_id, _ = create_channels
    message = "imagine"

    send_message_data = requests.post(config.url + 'message/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

    message_id = json.loads(send_message_data.text)['message_id']

    query_str = 'imag'

    search = requests.get(config.url + 'search/v1', params={
        'token': token,
        'query_str': query_str
    })

    get_search = json.loads(search.text)['messages']

    assert get_search[0]['message_id'] == message_id
    assert get_search[0]['u_id'] == user
    assert get_search[0]['message'] == message
    assert get_search[0]['reacts'] == [{'is_this_user_reacted': False, 'react_id': 1, 'u_ids': []}]
    assert get_search[0]['is_pinned'] == False


# ___COMPLEX TEST CASES - DEPENDANT FUNCTIONS___ #


def test_channel_and_dm_query(clear_data, create_users, create_channels, create_dms):
    token, user, _, _, _, _, = create_users
    channel_id, _ = create_channels
    dm_id, _, _ = create_dms
    message = "imagine"

    send_message_data = requests.post(config.url + 'message/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

    message_id = json.loads(send_message_data.text)['message_id']

    message_data = requests.post(config.url + 'message/senddm/v1', json={'token': token,
                                                                         'dm_id': dm_id,
                                                                         'message': message
                                                                         })

    dm_message_id = json.loads(message_data.text)['message_id']

    query_str = 'imag'

    search = requests.get(config.url + 'search/v1', params={
        'token': token,
        'query_str': query_str
    })

    get_search = json.loads(search.text)['messages']

    assert get_search[0]['message_id'] == message_id
    assert get_search[0]['u_id'] == user
    assert get_search[0]['message'] == message
    assert get_search[0]['reacts'] == [{'is_this_user_reacted': False, 'react_id': 1, 'u_ids': []}]
    assert get_search[0]['is_pinned'] == False

    assert get_search[1]['message_id'] == dm_message_id
    assert get_search[1]['u_id'] == user
    assert get_search[1]['message'] == message
    assert get_search[1]['reacts'] == [{'is_this_user_reacted': False, 'react_id': 1, 'u_ids': []}]
    assert get_search[1]['is_pinned'] == False


def test_multiple_channels_and_dms(clear_data, create_users, create_channels, create_dms):
    token_1, user_1, token_2, user_2, token_3, _, = create_users
    channel_id_1, channel_id_2 = create_channels
    dm_id_1, dm_id_2, _ = create_dms
    message_1 = "imagine"
    message_2 = "imagine dragon"
    message_3 = "deez peanuts"
    message_4 = "not"

    send_message_data = requests.post(config.url + 'message/send/v1', json={
        'token': token_1,
        'channel_id': channel_id_1,
        'message': message_1
    })

    message_id_1 = json.loads(send_message_data.text)['message_id']

    send_message_data = requests.post(config.url + 'message/send/v1', json={
        'token': token_1,
        'channel_id': channel_id_2,
        'message': message_3
    })

    message_data_1 = requests.post(config.url + 'message/senddm/v1', json={'token': token_2,
                                                                           'dm_id': dm_id_1,
                                                                           'message': message_2
                                                                           })

    dm_message_id_1 = json.loads(message_data_1.text)['message_id']

    message_data_1 = requests.post(config.url + 'message/senddm/v1', json={'token': token_3,
                                                                           'dm_id': dm_id_2,
                                                                           'message': message_4
                                                                           })

    query_str = 'in'

    search = requests.get(config.url + 'search/v1', params={
        'token': token_1,
        'query_str': query_str
    })

    get_search = json.loads(search.text)['messages']

    assert get_search[0]['message_id'] == message_id_1
    assert get_search[0]['u_id'] == user_1
    assert get_search[0]['message'] == message_1
    assert get_search[0]['reacts'] == [{'is_this_user_reacted': False, 'react_id': 1, 'u_ids': []}]
    assert get_search[0]['is_pinned'] == False

    assert get_search[1]['message_id'] == dm_message_id_1
    assert get_search[1]['u_id'] == user_2
    assert get_search[1]['message'] == message_2
    assert get_search[1]['reacts'] == [{'is_this_user_reacted': False, 'react_id': 1, 'u_ids': []}]
    assert get_search[1]['is_pinned'] == False


# ___TEST VALID INPUT___ #


def test_query_too_short(clear_data, create_users, create_channels):
    token, _, _, _, _, _, = create_users
    _, _ = create_channels
    query_str = ''

    search = requests.get(config.url + 'search/v1', params={
        'token': token,
        'query_str': query_str
    })

    assert search.status_code == 400


def test_query_too_long(clear_data, create_users, create_channels):
    token, _, _, _, _, _, = create_users
    _, _ = create_channels
    query_str = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam nec sagittis sem, id aliquet est. Maecenas dignissim gravida enim at vehicula,\
                Vestibulum non ullamcorper ante. Integer pellentesque placerat urna et mollis. Donec ornare, nisl id fringilla suscipit, diam diam viverra nibh, \
                aliquet lacinia diam ipsum ac nunc. Suspendisse aliquet dolor pretium mi ornare, non egestas purus tempus. Proin ut eros venenatis, vestibulum nunc at, pretium orci,\
                Quisque convallis purus feugiat nisl fermentum euismod. Nunc ornare ultricies leo sit amet vehicula. Sed at sem nibh. Integer pellentesque ac libero ac semper.\
                Vestibulum laoreet blandit felis, ac mattis erat dignissim vitae. In ut quam at urna placerat ultricies. Pellentesque nibh velit, interdum sit amet risus sed,\
                mollis sagittis nulla. Suspendisse leo justo, congue a varius vitae, venenatis at ipsum. Nunc porttitor velit et porttitor pretium. Duis in lacus et lorem feugiat,\
                cursus pulvinar non augue. Morbi non est nibh. Sed non tincidunt leo, non condimentum felis. Nunc mattis rutrum fringilla. Morbi ultricies ornare felis, at vulputate risus\
                mollis sed. Sed a dapibus neque, Etiam blandit egestas erat eget rutrum. Nunc scelerisque nulla est, vehicula lacinia leo dapibus quis. Duis eleifend diam ipsum, vitae \
                pretium lorem euismod sed. Duis vel'

    search = requests.get(config.url + 'search/v1', params={
        'token': token,
        'query_str': query_str
    })

    assert search.status_code == 400


# ___TEST ACCESS PERMISSIONS ___ #


def test_invalid_token(clear_data, create_users, create_channels):
    token, _, _, _, _, _, = create_users
    channel_id, _ = create_channels
    message = "imagine"

    requests.post(config.url + 'message/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

    query_str = 'imagine'

    search = requests.get(config.url + 'search/v1', params={
        'token': 'token',
        'query_str': query_str
    })
    assert search.status_code == 403
