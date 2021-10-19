import pytest

from src.error import InputError
from src.other import clear_v1
import requests
from src import config
import json

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


@pytest.fixture
def create_data():
    # register a user and log them in
    requests.post(config.url + 'auth/register/v2', json={'email': 'hello@mycompany.com',
                                                         'password': 'mypassword',
                                                         'name_first': 'Firstname',
                                                         'name_last': 'Lastname'
                                                         })
    # get the user's id
    user_id_data = requests.post(config.url + 'auth/login/v2', json={'email': 'hello@mycompany.com',
                                                                     'password': 'mypassword'
                                                                     })
    auth_user_id = json.loads(user_id_data.text)['auth_user_id']

    return auth_user_id


def test_basic_case(clear_data, create_data):
    auth_user_id = create_data
    assert type(auth_user_id) == int


def test_multiple_emails(clear_data, create_data):
    auth_user_id = create_data
    # register a user and log them in
    requests.post(config.url + 'auth/register/v2', json={'email': 'new@mycompany.com',
                                                         'password': 'anotherpassword',
                                                         'name_first': 'Firstname',
                                                         'name_last': 'Lastname'
                                                         })
    # get the user's id
    user_id_data = requests.post(config.url + 'auth/login/v2', json={'email': 'new@mycompany.com',
                                                                     'password': 'anotherpassword'
                                                                     })
    user_id_1 = json.loads(user_id_data.text)['auth_user_id']

    assert type(auth_user_id) == int
    assert type(user_id_1) == int
    assert auth_user_id != user_id_1


def test_email_exists(clear_data):
    # get the user's id
    user_id_data = requests.post(config.url + 'auth/login/v2', json={'email': 'notreal@mycompany.com',
                                                                     'password': 'mypassword'
                                                                     })
    assert user_id_data.status_code == 400


def test_matching_password(clear_data, create_data):
    # get the user's id
    user_id_data = requests.post(config.url + 'auth/login/v2', json={'email': 'hello@mycompany.com',
                                                                     'password': 'notmyrealpassword'
                                                                    })
    assert user_id_data.status_code == 400

def test_login_second_user(clear_data, create_data):
    # register a user and log them in
    user_id_data = requests.post(config.url + 'auth/register/v2',
                                                    json={  'email': 'seconduser@mycompany.com',
                                                            'password': 'mypassword',
                                                            'name_first': 'Firstname',
                                                            'name_last': 'Lastname'
                                                    })

    user_id_1 = json.loads(user_id_data.text)['auth_user_id']
    # get the user's id
    user_id_data = requests.post(config.url + 'auth/login/v2',
                                                json={  'email': 'hello@mycompany.com',
                                                        'password': 'notmyrealpassword'
                                                })
    user_id_2 = json.loads(user_id_data.text)['auth_user_id']

    assert user_id_1 == user_id_2