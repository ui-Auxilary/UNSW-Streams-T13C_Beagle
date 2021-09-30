import pytest

from src.error import InputError
from src.other import clear_v1
from src.auth import auth_login_v1, auth_register_v1

'''
EMAIL_EXISTS
    - The entered email corresponds to an instance in the database 'user_emails'

MATCHING_PASSWORD
    - Entered password matches the user's password of corresponding email

    - Email belongs to user but wrong password
    - Email is not in the system
    - Email and password is correct
    - Logs in multiple users

ACCESS ERROR
    - User does not exist
'''

@pytest.fixture
def clear_data():
    clear_v1()

def test_basic_case(clear_data):
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']
    assert type(user_id) == int

def test_multiple_emails(clear_data):
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    auth_register_v1('new@mycompany.com', 'anotherpassword', 'Firstname', 'Lastname')
    user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']
    user_id_1 = auth_login_v1('new@mycompany.com', 'anotherpassword')['auth_user_id']
    assert type(user_id) == int
    assert type(user_id_1) == int
    assert user_id != user_id_1

def test_email_exists(clear_data):
    with pytest.raises(InputError):
        auth_login_v1('hello@mycompany.com', 'mypassword')

def test_matching_password(clear_data):
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    with pytest.raises(InputError):
        auth_login_v1('hello@mycompany.com', 'notmyrealpassword')
