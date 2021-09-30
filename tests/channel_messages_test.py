import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1

'''
InputError when any of:  
    channel_id does not refer to a valid channel
    start is greater than the total number of messages in the channel
    when there are no messages
      
AccessError when:
    channel_id is valid and the authorised user is not a member of the channel
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

def test_channel_messages_no_messages(clear_data, create_user_and_channel):
    auth_user_id, channel_id, messages = create_user_and_channel
    start = 0
    end = -1

    with pytest.raises(InputError):
        ## cannot display any messages if there are none
        channel_messages_v1(auth_user_id, channel_id, start)

def test_start_greater_than_total_messages(clear_data, create_user_and_channel):
    auth_user_id, channel_id, messages = create_user_and_channel
    start = 999

    with pytest.raises(InputError):
        ## start is greater than the total number of messages in the channel
        channel_messages_v1(auth_user_id, channel_id, start)

def test_invalid_channel_id(clear_data, create_user_and_channel):
    auth_user_id, channel_id, messages = create_user_and_channel
    start = 0
    invalid_channel_id = 222

    with pytest.raises(InputError):
        ## invites user to a non-existent channel
        channel_messages_v1(auth_user_id, invalid_channel_id, start)

def test_auth_user_not_member(clear_data, create_user_and_channel):
    auth_user_id, channel_id, messages = create_user_and_channel
    start = 0
    auth_register_v1('HELLO@mycompany.com', 'mypassword1', 'Firstnamee', 'Lastnamee')
    user_id_3 = auth_login_v1('HELLO@mycompany.com', 'mypassword1')['auth_user_id']

    ## checks that auth_user_id is not a member of the channel
    with pytest.raises(AccessError):
        channel_messages_v1(user_id_3, channel_id, start)

@pytest.mark.skip('This cannot be tested at Iteration 1')
def test_channel_messages_simple_case(clear_data, create_user_and_channel):
    '''
    auth_user_id, channel_id, messages = create_user_and_channel

    start = 0
    end = start + 50

    assert channel_messages_v1(auth_user_id, channel_id, start) == {'messages': messages, 'start': start, 'end': end}
    '''
    pass