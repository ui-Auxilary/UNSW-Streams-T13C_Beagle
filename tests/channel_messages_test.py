import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1

'''
INVALID_INPUT
    - channel_id does not refer to a valid channel
    - start is greater than the total number of messages in the channel
    when there are no messages

ACCESS_ERROR
    - channel_id is valid and the authorised user is not a member of the channel
'''

@pytest.fixture
def clear_data():
    clear_v1()

@pytest.fixture
def create_user_and_channel():
    ## register user, log them in and get their user_id
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    auth_user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']

    ## create a channel with that user
    channel_id = channels_create_v1(auth_user_id, 'channel_1', 'True')['channel_id']

    ## stores an array of messages
    messages = []

    return auth_user_id, channel_id, messages

def test_auth_user_id_exists(clear_data, create_user_and_channel):
    _, channel_id, _ = create_user_and_channel
    start = 0

    ## auth_user does not exist
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': str(213),
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })

    assert channel_messages_data.status_code == 403

def test_channel_messages_no_messages(clear_data, create_user_and_channel):
    auth_user_id, channel_id, _ = create_user_and_channel
    start = 0
    end = -1

    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })
    print(json.loads(channel_messages_data.text))
    assert channel_messages_data == {
        'messages': [],
        'start': start,
        'end': end,
    }

def test_start_greater_than_total_messages(clear_data, create_user_and_channel):
    auth_user_id, channel_id, _ = create_user_and_channel
    start = 999

    ## start is greater than the total number of messages in the channel
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })
    
    assert channel_messages_data.status_code == 403

def test_invalid_channel_id(clear_data, create_user_and_channel):
    auth_user_id, _, _ = create_user_and_channel
    start = 0
    invalid_channel_id = 222

    ## invites user to a non-existent channel
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': token,
                                                                                    'channel_id': invalid_channel_id,
                                                                                    'start': start
                                                                                    })

    assert channel_messages_data.status_code == 403

def test_auth_user_not_member(clear_data, create_user_and_channel):
    _, channel_id, _ = create_user_and_channel
    start = 0

    ## register new user that's not a member of the channel
    auth_register_v1('HELLO@mycompany.com', 'mypassword1', 'Firstnamee', 'Lastnamee')
    user_id_3 = auth_login_v1('HELLO@mycompany.com', 'mypassword1')['auth_user_id']

    ## checks that auth_user_id is not a member of the channel
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })

    assert channel_messages_data.status_code == 403
    
## ACCESS AND INPUT ERROR OVERLAP TESTS
def test_user_not_member_and_invalid_start(clear_data, create_user_and_channel):
    _, channel_id, _ = create_user_and_channel
    start = 10
    
    ## register new user that's not a member of the channel
    auth_register_v1('HELLO@mycompany.com', 'mypassword1', 'Firstnamee', 'Lastnamee')
    user_id_3 = auth_login_v1('HELLO@mycompany.com', 'mypassword1')['auth_user_id']

    ## invalid start and user is not a member of the channel
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })
    
    assert channel_messages_data.status_code == 403

def test_send_message(clear_data, create_user_and_channel):
    token, channel_id, _ = create_user_and_channel
    start = 0
    
    # make a message
    message_data = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                        'channel_id': channel_id,
                                                                        'message': 'i love testing so much im definitely not crying'
                                                                        })

    assert message_data.status_code == 200

    # read the message
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })

    start =  json.loads(channel_messages_data.text)['start']
    message = json.loads(channel_messages_data.text)['messages'][start]['message']

    assert message == 'i love testing so much im definitely not crying'

def test_send_multiple_messages(clear_data, create_user_and_channel):
    token, channel_id, _ = create_user_and_channel
    start = 0
    
    # make a message
    requests.post(config.url + 'message/send/v1', params={'token': token,
                                                        'channel_id': channel_id,
                                                        'message': 'one'
                                                        })

    requests.post(config.url + 'message/send/v1', params={'token': token,
                                                        'channel_id': channel_id,
                                                        'message': 'two'
                                                        })

    # read the message
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })

    start =  json.loads(channel_messages_data.text)['start']
    message = json.loads(channel_messages_data.text)['messages'][start]['message']
    assert message == 'one'
    message = json.loads(channel_messages_data.text)['messages'][start + 1]['message']
    assert message == 'two'

def test_send_many_messages(clear_data, create_user_and_channel):
    token, channel_id, _ = create_user_and_channel
    start = 0
    
    # make a message
    for message in range(0, 50):
        requests.post(config.url + 'message/send/v1', params={'token': token,
                                                            'channel_id': channel_id,
                                                            'message': str(message)
                                                            })
    
    # read the message
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })

    start =  json.loads(channel_messages_data.text)['start']

    for index in range(0, 50):
        message = json.loads(channel_messages_data.text)['messages'][index]['message']
        assert message == str(index)

def test_send_too_many_messages(clear_data, create_user_and_channel):
    token, channel_id, _ = create_user_and_channel
    start = 0
    
    # make a message
    for message in range(50, -1, -1):
        requests.post(config.url + 'message/send/v1', params={'token': token,
                                                            'channel_id': channel_id,
                                                            'message': str(message)
                                                            })
    
    # read the message
    channel_messages_data = requests.get(config.url + 'channel/messages/v2', params={'token': token,
                                                                                    'channel_id': channel_id,
                                                                                    'start': start
                                                                                    })

    start =  json.loads(channel_messages_data.text)['start']
    end =  json.loads(channel_messages_data.text)['end']

    for index in range(start, end):
        message = json.loads(channel_messages_data.text)['messages'][index]['message']
        assert message == str(index)

@pytest.mark.skip('This cannot be tested at Iteration 1')
def test_channel_messages_simple_case(clear_data, create_user_and_channel):
    '''
    auth_user_id, channel_id, messages = create_user_and_channel

    start = 0
    end = start + 50

    assert channel_messages_v1(auth_user_id, channel_id, start) == {'messages': messages, 'start': start, 'end': end}
    '''
    pass
