import pytest

from src import config
import requests
import json

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def create_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={
        'email': 'dhruv.gravity@gmail.com',
        'password': 'mypassword',
        'name_first': 'Firstname',
        'name_last': 'Lastname'
    })

    # stores a token
    token = json.loads(register_data.text)['token']
    auth_user_id = json.loads(register_data.text)['auth_user_id']

    return token, auth_user_id

def test_simple_case(clear_data, create_data):
    login_request = requests.post(config.url + 'auth/login/v2', json={
        'email': 'dhruv.gravity@gmail.com',
        'password': 'mypassword',
    })

    assert login_request.status_code == 200

    requests.post(config.url + 'auth/register/v2', json={
        'email': 'newuser@gmail.com',
        'password': 'mypassword',
        'name_first': 'Firstname',
        'name_last': 'Lastname'
    })


    requests.post(config.url + 'auth/passwordreset/request/v1', json={
        'email': 'dhruv.gravity@gmail.com'
    })

    data_source = requests.get(config.url + 'getdata/v1')
    data_source = json.loads(data_source.text)

    reset_key = list(data_source['password_reset_key'].keys())[0]

    requests.post(config.url + 'auth/passwordreset/reset/v1', json={
        'reset_code': reset_key,
        'new_password': 'thisisanewpassword'
    })

    login_request = requests.post(config.url + 'auth/login/v2', json={
        'email': 'dhruv.gravity@gmail.com',
        'password': 'mypassword',
    })

    assert login_request.status_code == 400

    login_request = requests.post(config.url + 'auth/login/v2', json={
        'email': 'dhruv.gravity@gmail.com',
        'password': 'thisisanewpassword',
    })

    assert json.loads(login_request.text)['auth_user_id'] == 1

def test_email_nonexistent(clear_data, create_data):
    reset_request = requests.post(config.url + 'auth/passwordreset/request/v1', json={
        'email': 'randomperson10920132@gmail.com'
    })

    assert reset_request.status_code == 200

def test_resetcode_nonexistent(clear_data, create_data):
    reset_request = requests.post(config.url + 'auth/passwordreset/reset/v1', json={
        'reset_code': '23432',
        'new_password': 'thisisanewpassword'
    })

    assert reset_request.status_code == 400

def test_short_password(clear_data, create_data):
    login_request = requests.post(config.url + 'auth/login/v2', json={
        'email': 'dhruv.gravity@gmail.com',
        'password': 'mypassword',
    })

    assert login_request.status_code == 200

    requests.post(config.url + 'auth/passwordreset/request/v1', json={
        'email': 'dhruv.gravity@gmail.com'
    })

    data_source = requests.get(config.url + 'getdata/v1')
    data_source = json.loads(data_source.text)

    reset_key = list(data_source['password_reset_key'].keys())[0]

    reset_request = requests.post(config.url + 'auth/passwordreset/reset/v1', json={
        'reset_code': reset_key,
        'new_password': 'short'
    })

    assert reset_request.status_code == 400