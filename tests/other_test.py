import pytest 

from src.other import clear_v1
from src.auth import auth_login_v1, auth_register_v1
from src.channels import channels_create_v1

'''
TESTS
    - Right output for clear_v1
    - Create users and clear
    - Create multiple channels and clear
'''

@pytest.fixture
def register_login_users():
    ## register users, log them in and get their user_id
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id_1 = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']    
    auth_register_v1('sam@mycompany.com', 'mypassword', 'Samantha', 'Tse')
    user_id_2 = auth_login_v1('sam@mycompany.com', 'mypassword')['auth_user_id']

    return user_id_1, user_id_2

@pytest.fixture
def create_multiple_channels(register_login_users):
    user_id, user_id_2 = register_login_users

    ## create channels and get their ids
    channels_create_v1(user_id, 'Channel_1', True)['channel_id']
    channels_create_v1(user_id_2, 'Channel_2', True)['channel_id']
    channels_create_v1(user_id_2, 'Channel_3', False)['channel_id']

def test_valid_output_clear():
    ## check that it returns an empty dictionary
    assert clear_v1() == {}

def test_register_users_and_clear(register_login_users):
    assert clear_v1() == {}

def test_create_channels_and_clear(create_multiple_channels):
    assert clear_v1() == {}
