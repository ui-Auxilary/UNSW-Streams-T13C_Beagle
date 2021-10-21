# user_profile_setname(token, name_first, name_last):

import pytest

from src import config
import requests
import json


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


def test_simple_case(clear_data):
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'hello@mycompany.com',
                                                                         'password': 'mypassword',
                                                                         'name_first': 'Firstname',
                                                                         'name_last': 'Lastname'
                                                                         })

    # stores a token
    token = json.loads(register_data.text)['token']
    user_id = json.loads(register_data.text)['auth_user_id']
    name_first = 'Newname'
    name_last = 'Lastname'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 200

    # verify that the new handle is set
    user_info = requests.get(config.url + 'user/profile/v1', params={'token': token,
                                                                     'u_id': user_id})

    new_name = json.loads(user_info.text)['user']['name_first']
    new_last = json.loads(user_info.text)['user']['name_last']

    assert new_name == 'Newname'
    assert new_last == 'Lastname'


def test_firstname_exact_50_char(clear_data):
   # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HELsdfLO@mycompany.com',
                                                                         'password': 'MYpafsdssword',
                                                                         'name_first': 'jmqgushpmocvxsfykpnkmrsmtaqfabzahzbjnzcoyoxuwzoido',
                                                                         'name_last': 'LastsfNAME'
                                                                         })

    # stores a token
    token = json.loads(register_data.text)['token']
    name_first = 'jmqgushpmocvxsfykpnkmrsmtaqfabzahzbjnzcoyoxuwzoido'
    name_last = 'LastsfNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 200


def test_lastname_exact_50_char(clear_data):
   # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HELsdfLO@mycompany.com',
                                                                         'password': 'MYpafsdssword',
                                                                         'name_first': 'fsdsfd',
                                                                         'name_last': 'jmqgushpmocvxsfykpnkmrsmtaqfabzahzbjnzcoyoxuwzoido'
                                                                         })

    # stores a token
    token = json.loads(register_data.text)['token']
    name_first = 'fsdsfd'
    name_last = 'jmqgushpmocvxsfykpnkmrsmtaqfabzahzbjnzcoyoxuwzoido'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 200


def test_firstname_exact_1_char(clear_data):
   # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HELsdsdfLO@mycompany.com',
                                                                         'password': 'MYpadsfsdssword',
                                                                         'name_first': 'c',
                                                                         'name_last': 'gsffddgdf'
                                                                         })

    # stores a token
    token = json.loads(register_data.text)['token']
    name_first = 'c'
    name_last = 'gsffddgdf'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 200


def test_lastname_exact_1_char(clear_data):
   # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HElLofLO@mycompany.com',
                                                                         'password': 'MYsadasword',
                                                                         'name_first': 'ytfessd',
                                                                         'name_last': 'a'
                                                                         })

    # stores a token
    token = json.loads(register_data.text)['token']
    name_first = 'ytfessd'
    name_last = 'a'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 200


def test_firstname_less_than_1_char(clear_data):
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HdsLO@mycompany.com',
                                                                         'password': 'MYpafsdssword',
                                                                         'name_first': 'normal',
                                                                         'name_last': 'LastfdsNAME'
                                                                         })

    # stores a token
    token = json.loads(register_data.text)['token']
    name_first = ''
    name_last = 'LastfdsNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 400


def test_firstname_more_than_50_char(clear_data):
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HELLO@mycompany.com',
                                                                         'password': 'MYpassword',
                                                                         'name_first': 'FirswsedrftgyuijkygyuyuyuyE',
                                                                         'name_last': 'LastNAME'
                                                                         })

    # stores a token
    token = json.loads(register_data.text)['token']
    name_first = 'FirswsedrftgyuijkygyuyuyuyuyuygyuefseoftyguhijkfrtgyuhtNAME'
    name_last = 'LastNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 400


def test_lastname_less_than_1_char(clear_data):
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HdssdsfLO@mycompany.com',
                                                                         'password': 'MYpafffdssdssword',
                                                                         'name_first': 'normalname',
                                                                         'name_last': 'nromalname'
                                                                         })

    # stores a token
    token = json.loads(register_data.text)['token']
    name_first = 'normalname'
    name_last = ''

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 400


def test_lastname_more_than_50_char(clear_data):
   # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', json={'email': 'HELLO@mycompany.com',
                                                                         'password': 'MYpassword',
                                                                         'name_first': 'Firstihuiname',
                                                                         'name_last': 'LastsfdsdfsfjdsNAME'
                                                                         })

    # stores a token
    token = json.loads(register_data.text)['token']
    name_first = 'Firstihuiname'
    name_last = 'LastsfdsdfsfsdfdsdfsdsfdfsfdsdsdfssddssddfjskdlsdklskdljdsNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 400


def test_invalid_token_only(clear_data):
    token = str("dfssdfds")
    name_first = 'Firstihuiname'
    name_last = 'LastsfljdsNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_firstname_exact_50_char_and_invalid_token(clear_data):
   # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HELsdfLO@mycompany.com',
                                                         'password': 'MYpafsdssword',
                                                         'name_first': 'jmqgushpmocvxsfyxuwzoido',
                                                         'name_last': 'LastsfNAME'
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = 'jmqgushpmocvxsfykpnkmrsmtaqfabzahzbjnzcoyoxuwzoido'
    name_last = 'LastsfNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_lastname_over_50_char_and_invalid_token(clear_data):
   # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HELsdfLO@mycompany.com',
                                                         'password': 'MYpafsdssword',
                                                         'name_first': 'fsdsfd',
                                                         'name_last': 'jmqgushpmocvxsfykpnkmrsmtaqfabzahzbjnzcoyoxuwzoido'
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = 'fsdsfd'
    name_last = 'jmqgushpmocvxsfykpsadfdsafdsafsafsadasffdankmrsmtaqfabzahzbjnzcoyoxuwzoido'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_firstname_exact_1_char_and_invalid_token(clear_data):
   # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HELsdsdfLO@mycompany.com',
                                                         'password': 'MYpadsfsdssword',
                                                         'name_first': 'c',
                                                         'name_last': 'gsffddgdf'
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = 'c'
    name_last = 'gsffddgdf'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_lastname_exact_1_char_and_invalid_token(clear_data):
   # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HElLofLO@mycompany.com',
                                                         'password': 'MYsadasword',
                                                         'name_first': 'ytfessd',
                                                         'name_last': 'a'
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = 'ytfessd'
    name_last = 'a'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_firstname_less_than_1_char_and_invalid_token(clear_data):
    # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HdsLO@mycompany.com',
                                                         'password': 'MYpafsdssword',
                                                         'name_first': '',
                                                         'name_last': 'LastfdsNAME'
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = ''
    name_last = 'LastfdsNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_firstname_more_than_50_char_and_invalid_token(clear_data):
    # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HELLO@mycompany.com',
                                                         'password': 'MYpassword',
                                                         'name_first': 'FirswsedrftgyuijkygyuyuyuyuyuygyuefseoftyguhijkfrtgyuhtNAME',
                                                         'name_last': 'LastNAME'
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = 'FirswsedrftgyuijkygyuyuyuyuyuygyuefseoftyguhijkfrtgyuhtNAME'
    name_last = 'LastNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_lastname_less_than_1_char_and_invalid_token(clear_data):
    # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HdssdsfLO@mycompany.com',
                                                         'password': 'MYpafffdssdssword',
                                                         'name_first': 'normalname',
                                                         'name_last': ''
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = 'normalname'
    name_last = ''

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_lastname_more_than_50_char_and_invalid_token(clear_data):
   # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HELLO@mycompany.com',
                                                         'password': 'MYpassword',
                                                         'name_first': 'Firstihuiname',
                                                         'name_last': 'LastsfdsdfsfsdfdsdfsdsfdfsfdsdsdfssddssddfjskdlsdklskdljdsNAME'
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = 'Firstihuiname'
    name_last = 'LastsfdsdfsfsdfdsdfsdsfdfsfdsdsdfssddssddfjskdlsdklskdljdsNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_firstname_invalid_char_and_invalid_token(clear_data):
   # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HELLO@mycompany.com',
                                                         'password': 'MYpassword',
                                                         'name_first': 'F$*965ame',
                                                         'name_last': 'LastjdsNAME'
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = 'F$*965ame'
    name_last = 'LastjdsNAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403


def test_lastname_invalid_char_and_invalid_token(clear_data):
   # register user, log them in and get their user_id
    requests.post(config.url + 'auth/register/v2', json={'email': 'HELLO@mycompany.com',
                                                         'password': 'MYpassword',
                                                         'name_first': 'fjkwnwekjnk',
                                                         'name_last': 'La^%57NAME'
                                                         })

    # stores a token
    token = str("sfjjfsd")
    name_first = 'fjkwnwekjnk'
    name_last = 'La^%57NAME'

    resp = requests.put(config.url + 'user/profile/setname/v1', json={'token': token,
                                                                      'name_first': name_first,
                                                                      'name_last': name_last
                                                                      })

    assert resp.status_code == 403
