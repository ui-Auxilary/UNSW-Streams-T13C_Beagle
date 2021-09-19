from src.other import clear_v1
import pytest

from src.data_store import data_store
from src.auth import auth_register_v1
from src.error import InputError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.channel import channel_join_v1
from src.auth import auth_login_v1

'''
VALID INPUT
    - invalid channel_id
    - user already in channel

ACCESS ERROR
    - channel is private AND user is not GLOBAL owner

'''

@pytest.fixture
def clear_data():
    clear_v1()


def test_simple_case(clear_data):
    # register user, log them in and get their user_id
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']

    # create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', 'True')['channel_id']

    # createa a new user
    auth_register_v1('sam@mycompany.com', 'mypassword', 'Samantha', 'Tse')
    new_user_id = auth_login_v1('sam@mycompany.com', 'mypassword')['auth_user_id']

    # get them to join the channel
    channel_join_v1(new_user_id, channel_id)

    # get the database
    data_source = data_store.get()
    # check that both users are members now
    assert data_source['channel_data']['members'] == [user_id, new_user_id]

def test_invalid_channel_id(clear_data):
    # register user, log them in and get their user_id
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']

    with pytest.raises(InputError):
        channel_join_v1(user_id, 234)


def test_user_already_in_channel(clear_data):
    # register user, log them in and get their user_id
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']

    # create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', 'True')['channel_id']
    with pytest.raises(InputError):
        # get them to join the channel again
        channel_join_v1(user_id, channel_id)

def test_private_not_global_owner(clear_data):
    # register user, log them in and get their user_id
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']
    
    # create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', 'False')['channel_id']

    # createa a new user
    auth_register_v1('sam@mycompany.com', 'mypassword', 'Samantha', 'Tse')
    new_user_id = auth_login_v1('sam@mycompany.com', 'mypassword')['auth_user_id']

    # get them to join the channel
    channel_join_v1(new_user_id, channel_id)

    # get the database
    data_source = data_store.get()
    # check that both users are members now
    assert data_source['channel_data']['members'] == [user_id, new_user_id]