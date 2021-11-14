import pytest

from src import config
import requests
import json

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_data(clear_data):
    # register a user and log them in
    user_id_data = requests.post(config.url + 'oauth/register/v1', json={'email': 'hello@mycompany.com',
                                                         'password': 'mypassword',
                                                         'name_first': 'Firstname',
                                                         'name_last': 'Lastname'
                                                         })

    auth_user_id = json.loads(user_id_data.text)['auth_user_id']
    token = json.loads(user_id_data.text)['token']

    return auth_user_id, token

def test_simple_register(create_data):
    auth_user_id, token = create_data
    assert type(auth_user_id) == int

def test_simple_login(create_data):
    original_id, _ = create_data
    user_id_data = requests.post(config.url + 'oauth/register/v1', json={'email': 'hello@mycompany.com'})
    auth_user_id = json.loads(user_id_data.text)['auth_user_id']

    assert original_id == auth_user_id

