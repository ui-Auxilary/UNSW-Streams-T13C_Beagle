from src.other import clear_v1
import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.data_operations import get_user

'''
VALID_INPUT
    - Valid auth_user_id
    - Valid channel_id
    - Valid channel and user id however user not member of channel

VALID_OUTPUT
    - Return details of the channel
'''

@pytest.fixture
def clear_data():
    clear_v1()

@pytest.fixture
def create_user_and_channel():
    # register user, log them in and get their user_id
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    auth_user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']

    # create a channel with that user
    channel_id = channels_create_v1(auth_user_id, 'channel_1', 'True')['channel_id']
    return auth_user_id, channel_id

def test_simple_case(clear_data, create_user_and_channel):
    auth_user_id, channel_id = create_user_and_channel
    user_handle = get_user(auth_user_id)['user_handle']
    user_data = { 'u_id': auth_user_id,
                  'email': 'hello@mycompany.com',
                  'name_first': 'Firstname',
                  'name_last': 'Lastname',
                  'handle_str': user_handle }

    assert channel_details_v1(auth_user_id, channel_id) == { 'name'         : 'channel_1',
                                                             'is_public'    : True,
                                                             'owner_members': [user_data],
                                                             'all_members'  : [user_data] }

def test_invalid_auth_id(clear_data, create_user_and_channel):
    auth_user_id, channel_id = create_user_and_channel
    with pytest.raises(AccessError):
        channel_details_v1(25, channel_id)

def test_invalid_channel_id(clear_data, create_user_and_channel):
    auth_user_id, channel_id = create_user_and_channel
    with pytest.raises(InputError):
        channel_details_v1(auth_user_id, 25)

def test_user_not_channel_member(clear_data, create_user_and_channel):
    auth_user_id, channel_id = create_user_and_channel

    # create a new user and log them in
    auth_register_v1('hello2@mycompany.com', 'my2password', 'First2name', 'Last2name')
    auth_user_id = auth_login_v1('hello2@mycompany.com', 'my2password')['auth_user_id']

    with pytest.raises(AccessError):
        channel_details_v1(auth_user_id, channel_id)