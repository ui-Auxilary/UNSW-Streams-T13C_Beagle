import pytest

from src.error import InputError
from src.other import clear_v1
import requests
from src import config
import json

'''
VALID_INPUT
    - Valid email 
    - No duplicate emails
    - Len(Password) > 6 
    - 1 < len(first_name) < 50 
    - 1 < len(last_name) < 50 

GENERATE_HANDLE
    - Generate a handle for a unique user (first + last name) 
    - Append a number to a duplicate user
    - Is first + last name > 20 characters? 
    - Remove non-alphanumeric characters

VALID_OUTPUT
    - Return unique auth_user ID
'''


@pytest.fixture
def clear_data():
    clear_v1()


@pytest.fixture
def create_data():
    ## register a user and log them in
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'hello@mycompany.com',
                                                                         'password': 'mypassword',
                                                                         'name_first': 'Michael',
                                                                         'name_last': 'Gao'
                                                                         })
    ## get the user's id
    user_id_data = requests.post(config.url + 'auth/login/v2', json={'email': 'hello@mycompany.com',
                                                                     'password': 'mypassword'
                                                                     })
    auth_user_id = json.loads(user_id_data.text)['auth_user_id']

    return register_data, auth_user_id


def test_register_valid_output(clear_data, create_data):
    _, auth_user_id = create_data
    assert type(auth_user_id) == int


def test_register_invalid_email(clear_data):
    ## register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': '789ashd@!.com',
                                                                         'password': 'mahooo',
                                                                         'name_first': 'Michael',
                                                                         'name_last': 'Gao'
                                                                         })
    assert register_data.status_code == 400

    ## register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': '789ashd.com',
                                                                         'password': 'mahooo',
                                                                         'name_first': 'Michael',
                                                                         'name_last': 'Gao'
                                                                         })
    assert register_data.status_code == 400


def test_register_no_duplicates(clear_data, create_data):
    create_data
    register_data, _ = create_data
    assert register_data.status_code == 400


def test_register_length_password(clear_data):
    ## registers a user with a password less than 6 characters
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'mrmaxilikestoeat@gmail.com',
                                                                         'password': 'short',
                                                                         'name_first': 'Michael',
                                                                         'name_last': 'Gao'
                                                                         })
    assert register_data.status_code == 400


def test_register_length_firstname_invalid(clear_data):
    ## registers a user with a first name longer than 50 characters
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'mrmaxilikestoeat@gmail.com',
                                                                         'password': 'short',
                                                                         'name_first': 'MichaelangelooooGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuiooooo',
                                                                         'name_last': 'Gao'
                                                                         })
    assert register_data.status_code == 400

    ## registers a user with a first name longer less than one character
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'mrmaxilikestoeat@gmail.com',
                                                                         'password': 'short',
                                                                         'name_first': '',
                                                                         'name_last': 'Gao'
                                                                         })
    assert register_data.status_code == 400


def test_register_length_lastname_invalid(clear_data):
    ## registers a user with a last name longer than 50 characters
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'mrmaxilikestoeat@gmail.com',
                                                                         'password': 'short',
                                                                         'name_first': 'Michael',
                                                                         'name_last': 'Gaotfvygbuhnijmoknhbvgfcrtvybuhnijmkojnhbgvftcrdetfvgybhunjihbvgcfdxtfvgybuhnijnuhbvgfcrdrftgyuhvyyv'
                                                                         })
    assert register_data.status_code == 400

    ## registers a user with a last name longer less than one character
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'mrmaxilikestoeat@gmail.com',
                                                                         'password': 'short',
                                                                         'name_first': 'Michael',
                                                                         'name_last': ''
                                                                         })
    assert register_data.status_code == 400


def test_user_handle(clear_data, create_data):
    create_data
    login_data = requests.post(config.url + 'auth/login/v2', json={'email': 'hello@mycompany.com',
                                                                   'password': 'mypassword'
                                                                  })                                                                     
    user_token = json.loads(login_data.text)['token']

    ## create a channel with the user id
    channel_data = requests.post(config.url + 'channels/create/v2', json={'token': user_token,
                                                                          'name': 'channel_1',
                                                                          'is_public': True
                                                                          })
    channel_id = json.loads(channel_data.text)['channel_id']

    ## get the user's handle from the channel details
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={'token': user_token,
                                                                                  'channel_id': channel_id
                                                                                  })
    user_handle = json.loads(channel_detail_data.text)['owner_members'][0]['handle_str']

    assert user_handle == 'michaelgao'


def test_non_alphanumeric_handle(clear_data):
    ## registers a new user
    requests.post(config.url + 'auth/register/v2', json={'email': 'mrmaxilikestoeat@gmail.com',
                                                         'password': 'mahooo',
                                                         'name_first': 'm@h3**',
                                                         'name_last': 'thecharmander'
                                                        })
    login_data = requests.post(config.url + 'auth/login/v2', json={'email': 'mrmaxilikestoeat@gmail.com',
                                                                   'password': 'mahooo'
                                                                  })                                                                     
    user_token = json.loads(login_data.text)['token']

    ## create a channel with the user id
    channel_data = requests.post(config.url + 'channels/create/v2', json={'token': user_token,
                                                                          'name': 'channel_1',
                                                                          'is_public': True
                                                                          })
    channel_id = json.loads(channel_data.text)['channel_id']

    ## get the user's handle from the channel details
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={'token': user_token,
                                                                                  'channel_id': channel_id
                                                                                  })
    user_handle = json.loads(channel_detail_data.text)[
        'owner_members'][0]['handle_str']

    assert user_handle == 'mh3thecharmander'


def test_duplicate_user_handles(clear_data):
    ## registers multiple users
    requests.post(config.url + 'auth/register/v2', json={'email': 'dhruvgravity@gmail.com',
                                                         'password': 'yesdhruv2019',
                                                         'name_first': 'Dhruv',
                                                         'name_last': 'Gravity'
                                                        })
    requests.post(config.url + 'auth/register/v2', json={'email': 'poo@gmail.com',
                                                         'password': 'poopoo',
                                                         'name_first': 'Dhruv',
                                                         'name_last': 'Gravity'
                                                        })                                                    
    requests.post(config.url + 'auth/register/v2', json={'email': 'qwertyuiop@gmail.com',
                                                         'password': 'mahooo',
                                                         'name_first': 'Dhruv',
                                                         'name_last': 'Gravity'
                                                        })

    ## logins multiple users
    login_data_0 = requests.post(config.url + 'auth/login/v2', json={'email': 'dhruvgravity@gmail.com',
                                                                     'password': 'yesdhruv2019'
                                                                    })                                                                                                                         
    login_data_1 = requests.post(config.url + 'auth/login/v2', json={'email': 'poo@gmail.com',
                                                                     'password': 'poopoo'
                                                                    }) 
    login_data_2 = requests.post(config.url + 'auth/login/v2', json={'email': 'qwertyuiop@gmail.com',
                                                                     'password': 'mahooo'
                                                                    })                                                                
    ## Gets user's tokens
    user_token_0 = json.loads(login_data_0.text)['token']
    user_token_1 = json.loads(login_data_1.text)['token']
    user_token_2 = json.loads(login_data_2.text)['token']

    ## create multiple channels channel
    channel_data_0 = requests.post(config.url + 'channels/create/v2', json={'token': user_token_0,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    channel_data_1 = requests.post(config.url + 'channels/create/v2', json={'token': user_token_1,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    channel_data_2 = requests.post(config.url + 'channels/create/v2', json={'token': user_token_2,
                                                                            'name': 'channel_1',
                                                                            'is_public': True
                                                                            })
    channel_id_0 = json.loads(channel_data_0.text)['channel_id']
    channel_id_1 = json.loads(channel_data_1.text)['channel_id']
    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    ## get multiple user handles from the channel details
    channel_detail_data_0 = requests.get(config.url + 'channel/details/v2', params={'token': user_token_0,
                                                                                    'channel_id': channel_id_0
                                                                                    })
    channel_detail_data_1 = requests.get(config.url + 'channel/details/v2', params={'token': user_token_1,
                                                                                    'channel_id': channel_id_1
                                                                                    })
    channel_detail_data_2 = requests.get(config.url + 'channel/details/v2', params={'token': user_token_2,
                                                                                    'channel_id': channel_id_2
                                                                                    })                                                                              

    handle_user_0 = json.loads(channel_detail_data_0.text)['owner_members'][0]['handle_str']
    handle_user_1 = json.loads(channel_detail_data_1.text)['owner_members'][0]['handle_str']
    handle_user_2 = json.loads(channel_detail_data_2.text)['owner_members'][0]['handle_str']

    assert handle_user_0 == 'dhruvgravity'
    assert handle_user_1 == 'dhruvgravity0'
    assert handle_user_2 == 'dhruvgravity1'
