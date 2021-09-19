from src.other import clear_v1
import pytest

from src.data_store import data_store
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.channel import channel_join_v1, channel_invite_v1
from src.auth import auth_login_v1

'''
InputError when any of:   
    - channel_id does not exist
    - u_id does not exist
    - u_id is already member of the channel
      
AccessError when:
    - the authorised user is not a member of the channel
'''


@pytest.fixture
def clear_data():
    clear_v1()

def create_user_and_channel():
    # register user, log them in and get their user_id
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']

    # create a new user
    auth_register_v1('sam@mycompany.com', 'mypassword', 'Samantha', 'Tse')
    new_user_id = auth_login_v1('sam@mycompany.com', 'mypassword')['auth_user_id']

    # create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', 'True')['channel_id']

    return (user_id, new_user_id, channel_id)


def test_invite_channel_simple_case(clear_data):
    user_id, new_user_id, channel_id = create_user_and_channel()

    # get the database
    data_source = data_store.get()
    # check that both users are members now
    assert data_source['channel_data'][channel_id]['members'] == [user_id, new_user_id]

def test_invalid_channel_id(clear_data):
    user_id, new_user_id, channel_id = create_user_and_channel()
    invalid_channel_id = 222

    with pytest.raises(InputError):
        # invites user to a non-existent channel
        channel_invite_v1(user_id, invalid_channel_id, new_user_id)

def test_invalid_user(clear_data):
    user_id, new_user_id, channel_id = create_user_and_channel()
    invalid_new_user_id = 222

    with pytest.raises(InputError):
        # invites a non-existent user into the channel
        channel_invite_v1(user_id, channel_id, invalid_new_user_id)

def test_user_already_in_channel(clear_data):
    user_id, new_user_id, channel_id = create_user_and_channel()

    # adds new_user in to the channel
    channel_join_v1(new_user_id, channel_id)

    with pytest.raises(InputError):
        # invite an existing user
        channel_invite_v1(user_id, channel_id, new_user_id)

def test_auth_user_not_member(clear_data):
    user_id, new_user_id, channel_id = create_user_and_channel()

    # get the database
    data_source = data_store.get()

    # checks that that user_id is not a member of the channel
    with pytest.raises(AccessError):
        data_source['channel_data'][channel_id]['members'] != [user_id]