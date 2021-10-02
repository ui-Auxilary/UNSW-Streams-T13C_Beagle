import pytest 

from src.other import clear_v1, check_user_exists
from src.auth import auth_login_v1, auth_register_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1

'''
TESTS
    - Right output for clear_v1
    - Check_user_exists
'''

@pytest.fixture
def register_login_users():
    ## register users, log them in and get their user_id
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id_1 = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']    
    auth_register_v1('sam@mycompany.com', 'mypassword', 'Samantha', 'Tse')
    user_id_2 = auth_login_v1('sam@mycompany.com', 'mypassword')['auth_user_id']

    return user_id_1, user_id_2    

def test_valid_output_clear():
    ## check that it returns an empty dictionary
    assert clear_v1() == {}

def test_register_users_and_clear():
    ## check that it returns an empty dictionary
    assert clear_v1() == {}

def test_valid_output_clear():
    ## check that it returns an empty dictionary
    assert clear_v1() == {}

def test_valid_output_clear():
    ## check that it returns an empty dictionary
    assert clear_v1() == {}

